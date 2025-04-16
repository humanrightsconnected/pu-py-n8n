"""
Main Pulumi program for deploying n8n to Azure Kubernetes Service.
"""
import pulumi
from pulumi import ResourceOptions

from pu_py_n8n.aks_cluster import create_aks_cluster
from pu_py_n8n.config import N8nConfig
from pu_py_n8n.n8n_deployment import deploy_n8n


def main():
    """
    Main entry point for the n8n on Azure deployment.
    
    Creates the following resources:
    - Resource Group
    - Azure Kubernetes Service (AKS) Cluster
    - n8n deployment with PostgreSQL database
    """
    # Load configuration
    config = N8nConfig()

    # Create AKS cluster
    aks_cluster = create_aks_cluster(
        resource_group_name=config.resource_group_name,
        location=config.location,
        kubernetes_version=config.kubernetes_version,
        node_count=config.node_count,
        node_size=config.node_size,
    )

    # Deploy n8n to the AKS cluster
    n8n_deployment = deploy_n8n(
        aks_cluster=aks_cluster,
        postgres_password=config.postgres_password,
        n8n_encryption_key=config.n8n_encryption_key,
        n8n_jwt_secret=config.n8n_jwt_secret,
    )

    # Export important values
    pulumi.export("resource_group_name", config.resource_group_name)
    pulumi.export("kubernetes_cluster_name", aks_cluster.name)
    pulumi.export("n8n_service_endpoint", n8n_deployment.service_endpoint)
    pulumi.export("kubeconfig", aks_cluster.kubeconfig)


# Call the main function if this file is executed directly
if __name__ == "__main__":
    main()