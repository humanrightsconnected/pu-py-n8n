"""
Tests for the n8n deployment module.
"""
import pulumi
import pytest
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import PersistentVolumeClaim, Secret, Service

from pu_py_n8n.n8n_deployment import deploy_n8n


@pytest.mark.asyncio
async def test_n8n_deployment_creates_resources(aks_cluster_mock):
    """Test that the n8n deployment creates all required resources."""
    
    # Deploy n8n with test credentials
    deployment = deploy_n8n(
        aks_cluster=aks_cluster_mock,
        postgres_password="test-postgres-password",
        n8n_encryption_key="test-n8n-encryption-key",
        n8n_jwt_secret="test-n8n-jwt-secret",
    )
    
    # Verify all expected resources are created
    assert isinstance(deployment.postgres_deployment, Deployment)
    assert isinstance(deployment.postgres_service, Service)
    assert isinstance(deployment.postgres_pvc, PersistentVolumeClaim)
    assert isinstance(deployment.n8n_deployment, Deployment)
    assert isinstance(deployment.n8n_service, Service)
    assert isinstance(deployment.n8n_pvc, PersistentVolumeClaim)
    assert deployment.service_endpoint is not None


@pytest.mark.asyncio
async def test_postgres_configuration():
    """Test that PostgreSQL is configured correctly."""
    
    def check_postgres_deployment(args):
        deployment = args[0]
        spec = deployment.spec
        
        # Check replicas
        assert spec.replicas == 1
        
        # Check container image
        containers = spec.template["spec"]["containers"]
        assert len(containers) == 1
        assert containers[0]["image"] == "postgres:14"
        
        # Check port
        assert containers[0]["ports"][0]["containerPort"] == 5432
        
        # Check resource limits
        assert containers[0]["resources"]["limits"]["memory"] == "500Mi"
        assert containers[0]["resources"]["requests"]["memory"] == "250Mi"
        
        return True
    
    # Set up a resource check
    resource_check = pulumi.runtime.ResourceCheck()
    resource_check.register("kubernetes:apps/v1:Deployment", check_postgres_deployment, 
                            lambda args: args[0].metadata["name"] == "postgres")
    
    # Deploy n8n with test credentials
    deploy_n8n(
        aks_cluster=aks_cluster_mock,
        postgres_password="test-postgres-password",
        n8n_encryption_key="test-n8n-encryption-key",
        n8n_jwt_secret="test-n8n-jwt-secret",
    )
    
    # Wait for the resource check to complete
    await resource_check.wait()


@pytest.mark.asyncio
async def test_n8n_configuration():
    """Test that n8n is configured correctly."""
    
    def check_n8n_deployment(args):
        deployment = args[0]
        spec = deployment.spec
        
        # Check replicas
        assert spec.replicas == 1
        
        # Check container image
        containers = spec.template["spec"]["containers"]
        assert len(containers) == 1
        assert containers[0]["image"] == "n8nio/n8n:latest"
        
        # Check port
        assert containers[0]["ports"][0]["containerPort"] == 5678
        
        # Check resource limits
        assert containers[0]["resources"]["limits"]["memory"] == "500Mi"
        assert containers[0]["resources"]["requests"]["memory"] == "250Mi"
        
        # Check environment variables exist (we can't check values directly because they're from secrets)
        env_names = [env["name"] for env in containers[0]["env"]]
        required_env_vars = [
            "DB_TYPE", 
            "DB_POSTGRESDB_HOST", 
            "DB_POSTGRESDB_PORT",
            "DB_POSTGRESDB_DATABASE", 
            "DB_POSTGRESDB_USER", 
            "DB_POSTGRESDB_PASSWORD",
            "N8N_ENCRYPTION_KEY",
            "N8N_JWT_SECRET"
        ]
        
        for env_var in required_env_vars:
            assert env_var in env_names
        
        return True
    
    # Set up a resource check
    resource_check = pulumi.runtime.ResourceCheck()
    resource_check.register("kubernetes:apps/v1:Deployment", check_n8n_deployment, 
                            lambda args: args[0].metadata["name"] == "n8n")
    
    # Deploy n8n with test credentials
    deploy_n8n(
        aks_cluster=aks_cluster_mock,
        postgres_password="test-postgres-password",
        n8n_encryption_key="test-n8n-encryption-key",
        n8n_jwt_secret="test-n8n-jwt-secret",
    )
    
    # Wait for the resource check to complete
    await resource_check.wait()


@pytest.mark.asyncio
async def test_service_endpoint():
    """Test that the service endpoint is properly constructed."""
    
    # Deploy n8n with test credentials
    deployment = deploy_n8n(
        aks_cluster=aks_cluster_mock,
        postgres_password="test-postgres-password",
        n8n_encryption_key="test-n8n-encryption-key",
        n8n_jwt_secret="test-n8n-jwt-secret",
    )
    
    # Get the service endpoint
    endpoint = await deployment.service_endpoint.future()
    
    # Verify it's correctly formed
    assert endpoint.startswith("http://")
    assert "10.0.0.1" in endpoint  # This is the IP we set in the mock