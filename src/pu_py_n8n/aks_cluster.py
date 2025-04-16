"""
Module for creating and configuring an Azure Kubernetes Service (AKS) cluster.
"""
from dataclasses import dataclass

import pulumi
import pulumi_azure_native as azure_native
from pulumi_azure_native import containerservice, resources


@dataclass
class AksCluster:
    """
    Represents an AKS cluster resource and its related properties.
    """

    name: str
    resource_group: resources.ResourceGroup
    cluster: containerservice.ManagedCluster
    kubeconfig: pulumi.Output[str]


def create_aks_cluster(
    resource_group_name: str,
    location: str,
    kubernetes_version: str,
    node_count: int,
    node_size: str,
) -> AksCluster:
    """
    Create an Azure Kubernetes Service (AKS) cluster.

    Args:
        resource_group_name: Name of the resource group
        location: Azure region to deploy to
        kubernetes_version: Kubernetes version to use
        node_count: Number of nodes in the default node pool
        node_size: VM size for the nodes

    Returns:
        AksCluster: Object containing the created resources
    """
    # Create a resource group
    resource_group = resources.ResourceGroup(
        resource_group_name,
        resource_group_name=resource_group_name,
        location=location,
    )

    # Create AKS cluster
    cluster_name = f"{resource_group_name}-aks"
    managed_cluster = containerservice.ManagedCluster(
        cluster_name,
        resource_group_name=resource_group.name,
        location=resource_group.location,
        agent_pool_profiles=[
            containerservice.ManagedClusterAgentPoolProfileArgs(
                count=node_count,
                vm_size=node_size,
                mode="System",
                name="agentpool",
                os_type="Linux",
                type="VirtualMachineScaleSets",
            )
        ],
        dns_prefix=cluster_name,
        kubernetes_version=kubernetes_version,
        identity=containerservice.ManagedClusterIdentityArgs(
            type="SystemAssigned",
        ),
        enable_rbac=True,
    )

    # Get the kubeconfig from the created cluster
    creds = containerservice.get_managed_cluster_admin_credentials_output(
        resource_group_name=resource_group.name,
        resource_name=managed_cluster.name,
    )
    
    # The kubeconfig is the first item in the kubeconfigs array
    kubeconfig = creds.kubeconfigs[0].value

    return AksCluster(
        name=managed_cluster.name,
        resource_group=resource_group,
        cluster=managed_cluster,
        kubeconfig=kubeconfig,
    )