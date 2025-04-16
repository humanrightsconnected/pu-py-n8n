"""
Module for deploying n8n to an AKS cluster with PostgreSQL.
"""
import base64
from dataclasses import dataclass

import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
    ConfigMap,
    PersistentVolumeClaim,
    PersistentVolumeClaimSpecArgs,
    Secret,
    Service,
    ServiceSpecArgs,
)
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs

from pu_py_n8n.aks_cluster import AksCluster


@dataclass
class N8nDeployment:
    """
    Represents an n8n deployment on Kubernetes and its related resources.
    """

    postgres_deployment: Deployment
    postgres_service: Service
    postgres_pvc: PersistentVolumeClaim
    n8n_deployment: Deployment
    n8n_service: Service
    n8n_pvc: PersistentVolumeClaim
    service_endpoint: pulumi.Output[str]


def deploy_n8n(
    aks_cluster: AksCluster,
    postgres_password: str,
    n8n_encryption_key: str,
    n8n_jwt_secret: str,
) -> N8nDeployment:
    """
    Deploy n8n and PostgreSQL to an AKS cluster.

    Args:
        aks_cluster: AKS cluster to deploy to
        postgres_password: Password for PostgreSQL
        n8n_encryption_key: Encryption key for n8n
        n8n_jwt_secret: JWT secret for n8n authentication

    Returns:
        N8nDeployment: Object containing all deployed resources
    """
    # Create Kubernetes provider using the kubeconfig from the AKS cluster
    k8s_provider = k8s.Provider(
        "k8s-provider",
        kubeconfig=aks_cluster.kubeconfig,
    )
    provider_args = pulumi.ResourceOptions(provider=k8s_provider)

    # Common labels for all resources
    app_labels = {"app": "n8n"}

    # Create namespace for n8n
    namespace = k8s.core.v1.Namespace(
        "n8n-namespace",
        metadata=ObjectMetaArgs(name="n8n"),
        opts=provider_args,
    )
    namespace_name = namespace.metadata["name"]

    # Create PostgreSQL resources
    postgres_secret = Secret(
        "postgres-secret",
        metadata=ObjectMetaArgs(
            name="postgres-secret",
            namespace=namespace_name,
        ),
        string_data={
            "POSTGRES_PASSWORD": postgres_password,
            "POSTGRES_USER": "postgres",
            "POSTGRES_DB": "n8n",
        },
        opts=provider_args,
    )

    postgres_pvc = PersistentVolumeClaim(
        "postgres-pvc",
        metadata=ObjectMetaArgs(
            name="postgres-claim0",
            namespace=namespace_name,
        ),
        spec=PersistentVolumeClaimSpecArgs(
            access_modes=["ReadWriteOnce"],
            resources={"requests": {"storage": "1Gi"}},
        ),
        opts=provider_args,
    )

    postgres_deployment = Deployment(
        "postgres-deployment",
        metadata=ObjectMetaArgs(
            name="postgres",
            namespace=namespace_name,
        ),
        spec=DeploymentSpecArgs(
            selector=LabelSelectorArgs(match_labels={"app": "postgres"}),
            replicas=1,
            template={
                "metadata": {"labels": {"app": "postgres"}},
                "spec": {
                    "containers": [
                        {
                            "name": "postgres",
                            "image": "postgres:14",
                            "env": [
                                {
                                    "name": "POSTGRES_PASSWORD",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": postgres_secret.metadata["name"],
                                            "key": "POSTGRES_PASSWORD",
                                        }
                                    },
                                },
                                {
                                    "name": "POSTGRES_USER",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": postgres_secret.metadata["name"],
                                            "key": "POSTGRES_USER",
                                        }
                                    },
                                },
                                {
                                    "name": "POSTGRES_DB",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": postgres_secret.metadata["name"],
                                            "key": "POSTGRES_DB",
                                        }
                                    },
                                },
                            ],
                            "ports": [{"containerPort": 5432}],
                            "volumeMounts": [
                                {
                                    "name": "postgres-data",
                                    "mountPath": "/var/lib/postgresql/data",
                                }
                            ],
                            "resources": {
                                "limits": {"memory": "500Mi"},
                                "requests": {"memory": "250Mi"},
                            },
                        }
                    ],
                    "volumes": [
                        {
                            "name": "postgres-data",
                            "persistentVolumeClaim": {"claimName": postgres_pvc.metadata["name"]},
                        }
                    ],
                },
            },
        ),
        opts=provider_args,
    )

    postgres_service = Service(
        "postgres-service",
        metadata=ObjectMetaArgs(
            name="postgres",
            namespace=namespace_name,
        ),
        spec=ServiceSpecArgs(
            selector={"app": "postgres"},
            ports=[{"port": 5432}],
        ),
        opts=provider_args,
    )

    # Create n8n resources
    n8n_secret = Secret(
        "n8n-secret",
        metadata=ObjectMetaArgs(
            name="n8n-secret",
            namespace=namespace_name,
        ),
        string_data={
            "DB_TYPE": "postgresdb",
            "DB_POSTGRESDB_HOST": postgres_service.metadata["name"],
            "DB_POSTGRESDB_PORT": "5432",
            "DB_POSTGRESDB_DATABASE": "n8n",
            "DB_POSTGRESDB_USER": "postgres",
            "DB_POSTGRESDB_PASSWORD": postgres_password,
            "N8N_ENCRYPTION_KEY": n8n_encryption_key,
            "N8N_JWT_SECRET": n8n_jwt_secret,
        },
        opts=provider_args,
    )

    n8n_pvc = PersistentVolumeClaim(
        "n8n-pvc",
        metadata=ObjectMetaArgs(
            name="n8n-claim0",
            namespace=namespace_name,
        ),
        spec=PersistentVolumeClaimSpecArgs(
            access_modes=["ReadWriteOnce"],
            resources={"requests": {"storage": "1Gi"}},
        ),
        opts=provider_args,
    )

    n8n_deployment = Deployment(
        "n8n-deployment",
        metadata=ObjectMetaArgs(
            name="n8n",
            namespace=namespace_name,
        ),
        spec=DeploymentSpecArgs(
            selector=LabelSelectorArgs(match_labels={"app": "n8n"}),
            replicas=1,
            template={
                "metadata": {"labels": {"app": "n8n"}},
                "spec": {
                    "containers": [
                        {
                            "name": "n8n",
                            "image": "n8nio/n8n:latest",
                            "ports": [{"containerPort": 5678}],
                            "env": [
                                {
                                    "name": "DB_TYPE",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": n8n_secret.metadata["name"],
                                            "key": "DB_TYPE",
                                        }
                                    },
                                },
                                {
                                    "name": "DB_POSTGRESDB_HOST",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": n8n_secret.metadata["name"],
                                            "key": "DB_POSTGRESDB_HOST",
                                        }
                                    },
                                },
                                {
                                    "name": "DB_POSTGRESDB_PORT",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": n8n_secret.metadata["name"],
                                            "key": "DB_POSTGRESDB_PORT",
                                        }
                                    },
                                },
                                {
                                    "name": "DB_POSTGRESDB_DATABASE",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": n8n_secret.metadata["name"],
                                            "key": "DB_POSTGRESDB_DATABASE",
                                        }
                                    },
                                },
                                {
                                    "name": "DB_POSTGRESDB_USER",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": n8n_secret.metadata["name"],
                                            "key": "DB_POSTGRESDB_USER",
                                        }
                                    },
                                },
                                {
                                    "name": "DB_POSTGRESDB_PASSWORD",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": n8n_secret.metadata["name"],
                                            "key": "DB_POSTGRESDB_PASSWORD",
                                        }
                                    },
                                },
                                {
                                    "name": "N8N_ENCRYPTION_KEY",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": n8n_secret.metadata["name"],
                                            "key": "N8N_ENCRYPTION_KEY",
                                        }
                                    },
                                },
                                {
                                    "name": "N8N_JWT_SECRET",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": n8n_secret.metadata["name"],
                                            "key": "N8N_JWT_SECRET",
                                        }
                                    },
                                },
                            ],
                            "volumeMounts": [
                                {
                                    "name": "n8n-data",
                                    "mountPath": "/home/node/.n8n",
                                }
                            ],
                            "resources": {
                                "limits": {"memory": "500Mi"},
                                "requests": {"memory": "250Mi"},
                            },
                        }
                    ],
                    "volumes": [
                        {
                            "name": "n8n-data",
                            "persistentVolumeClaim": {"claimName": n8n_pvc.metadata["name"]},
                        }
                    ],
                },
            },
        ),
        opts=provider_args,
    )

    n8n_service = Service(
        "n8n-service",
        metadata=ObjectMetaArgs(
            name="n8n",
            namespace=namespace_name,
            annotations={
                "service.beta.kubernetes.io/azure-load-balancer-internal": "true",
            },
        ),
        spec=ServiceSpecArgs(
            type="LoadBalancer",
            selector={"app": "n8n"},
            ports=[{"port": 80, "targetPort": 5678}],
        ),
        opts=provider_args,
    )

    # Extract the service endpoint
    service_endpoint = pulumi.Output.concat(
        "http://", n8n_service.status.apply(lambda status: status.load_balancer.ingress[0].ip)
    )

    return N8nDeployment(
        postgres_deployment=postgres_deployment,
        postgres_service=postgres_service,
        postgres_pvc=postgres_pvc,
        n8n_deployment=n8n_deployment,
        n8n_service=n8n_service,
        n8n_pvc=n8n_pvc,
        service_endpoint=service_endpoint,
    )