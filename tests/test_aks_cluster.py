"""
Tests for the AKS cluster module.
"""
import pulumi
import pytest
from pulumi_azure_native import containerservice, resources

from pu_py_n8n.aks_cluster import create_aks_cluster


@pytest.mark.asyncio
async def test_resource_group_creation():
    """Test that the resource group is created with the correct properties."""
    
    def check_resource_group(args):
        resource_group = args[0]
        assert resource_group.resource_group_name == "test-resource-group"
        assert resource_group.location == "eastus"
        return True

    # Set up a resource check to validate properties
    resource_check = pulumi.runtime.ResourceCheck()
    resource_check.register("azure-native:resources:ResourceGroup", check_resource_group)
    
    # Create the AKS cluster
    cluster = create_aks_cluster(
        resource_group_name="test-resource-group",
        location="eastus",
        kubernetes_version="1.26.10",
        node_count=1,
        node_size="Standard_D2_v2",
    )
    
    # Wait for the resource check to complete
    await resource_check.wait()
    
    # Verify the cluster was created and has the expected properties
    assert cluster.name is not None
    assert cluster.resource_group is not None
    assert cluster.kubeconfig is not None


@pytest.mark.asyncio
async def test_aks_cluster_configuration():
    """Test that the AKS cluster is configured with the correct properties."""
    
    def check_aks_cluster(args):
        cluster = args[0]
        assert cluster.kubernetes_version == "1.26.10"
        assert len(cluster.agent_pool_profiles) == 1
        assert cluster.agent_pool_profiles[0].count == 1
        assert cluster.agent_pool_profiles[0].vm_size == "Standard_D2_v2"
        assert cluster.agent_pool_profiles[0].mode == "System"
        assert cluster.enable_rbac is True
        return True
    
    # Set up a resource check to validate properties
    resource_check = pulumi.runtime.ResourceCheck()
    resource_check.register("azure-native:containerservice:ManagedCluster", check_aks_cluster)
    
    # Create the AKS cluster
    cluster = create_aks_cluster(
        resource_group_name="test-resource-group",
        location="eastus",
        kubernetes_version="1.26.10",
        node_count=1,
        node_size="Standard_D2_v2",
    )
    
    # Wait for the resource check to complete
    await resource_check.wait()