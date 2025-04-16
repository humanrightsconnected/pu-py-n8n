"""
Pytest configuration and fixtures for testing n8n Azure deployment.
"""
import json
from unittest.mock import MagicMock

import pytest
import pulumi


# Set up mocks for Pulumi to allow testing without actually creating resources
class PulumiMocks(pulumi.runtime.Mocks):
    """
    Mocks for Pulumi to test infrastructure code without creating real resources.
    """

    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        """
        Create a mock resource and return predefined outputs.
        """
        # Return consistent resource IDs to ensure tests are deterministic
        resource_id = f"{args.name}_id"
        state = {
            "id": resource_id,
            # Add any other default properties needed for your resources
            "name": args.name,
            "urn": f"urn:pulumi:{args.stack}::{args.type}::{args.name}",
        }

        # Customize outputs for specific resource types
        if args.type == "azure-native:containerservice:ManagedCluster":
            state.update({
                "kubeConfigRaw": json.dumps({
                    "apiVersion": "v1",
                    "clusters": [{"cluster": {}, "name": "test-cluster"}],
                    "contexts": [{"context": {}, "name": "test-context"}],
                    "current-context": "test-context",
                    "kind": "Config",
                    "users": [{"name": "test-user", "user": {}}],
                }),
            })
        elif args.type == "kubernetes:core/v1:Service" and args.name == "n8n-service":
            state.update({
                "status": {
                    "loadBalancer": {
                        "ingress": [{"ip": "10.0.0.1"}]
                    }
                }
            })

        return resource_id, dict(args.inputs, **state)

    def call(self, args: pulumi.runtime.MockCallArgs):
        """
        Mock resource calls during testing.
        """
        # Handle specific calls
        if args.token == "azure-native:containerservice:getManagedClusterAdminCredentials":
            return {
                "kubeconfigs": [
                    {
                        "name": "test-cluster-admin",
                        "value": "YXBpVmVyc2lvbjogdjEK",  # Base64 encoded dummy kubeconfig
                    }
                ]
            }

        return {}


@pytest.fixture(scope="session", autouse=True)
def setup_pulumi_mocks():
    """
    Set up Pulumi mocks for all tests.
    
    This fixture runs once at the start of the test session and configures
    Pulumi to use our mocks instead of interacting with real cloud providers.
    """
    pulumi.runtime.set_mocks(PulumiMocks())


@pytest.fixture
def aks_cluster_mock():
    """
    Create a mock AKS cluster.
    """
    from pu_py_n8n.aks_cluster import AksCluster

    resource_group = MagicMock()
    resource_group.name = pulumi.Output.from_input("test-resource-group")
    
    cluster = MagicMock()
    cluster.name = pulumi.Output.from_input("test-aks-cluster")
    
    kubeconfig = pulumi.Output.from_input("test-kubeconfig-content")
    
    return AksCluster(
        name="test-aks-cluster",
        resource_group=resource_group,
        cluster=cluster,
        kubeconfig=kubeconfig,
    )