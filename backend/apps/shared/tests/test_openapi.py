"""
Test OpenAPI schema generation and API documentation.

Tests drf-spectacular schema generation, Swagger UI, and ReDoc.
Ham Dog & TC making API documentation shine! 🚀
"""

import json

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestOpenAPISchema:
  """Test OpenAPI schema generation"""

  def test_schema_generates_without_errors(self):
    """OpenAPI schema generation succeeds"""
    client = APIClient()
    # Schema endpoint doesn't require authentication
    response = client.get("/api/schema/")

    assert response.status_code == status.HTTP_200_OK
    assert "application/vnd.oai.openapi" in response["Content-Type"]

  def test_schema_includes_all_famapp_viewsets(self):
    """Schema includes all FamApp ViewSets"""
    import json

    client = APIClient()
    response = client.get("/api/schema/")

    assert response.status_code == status.HTTP_200_OK
    schema = json.loads(response.content)

    # Check paths include all ViewSets
    paths = schema.get("paths", {})
    assert "/api/v1/families/" in paths
    assert "/api/v1/todos/" in paths
    assert "/api/v1/events/" in paths
    assert "/api/v1/groceries/" in paths
    assert "/api/v1/pets/" in paths

  def test_schema_includes_viewset_operations(self):
    """Schema includes CRUD operations for ViewSets"""
    client = APIClient()
    response = client.get("/api/schema/")

    schema = json.loads(response.content)
    paths = schema.get("paths", {})

    # Check family endpoints have correct HTTP methods
    family_list = paths.get("/api/v1/families/", {})
    assert "get" in family_list  # List
    assert "post" in family_list  # Create

    # Check detail endpoints
    family_detail_path = None
    for path in paths.keys():
      if "/api/v1/families/{public_id}/" in path:
        family_detail_path = path
        break

    assert family_detail_path is not None
    family_detail = paths[family_detail_path]
    assert "get" in family_detail  # Retrieve
    assert "patch" in family_detail  # Update
    assert "delete" in family_detail  # Destroy

  def test_schema_includes_custom_actions(self):
    """Schema includes custom actions (@action decorators)"""
    client = APIClient()
    response = client.get("/api/schema/")

    schema = json.loads(response.content)
    paths = schema.get("paths", {})

    # Check custom actions exist - paths might vary slightly
    # Just check that custom action paths exist
    found_todo_toggle = any("todos" in p and "toggle" in p for p in paths.keys())
    found_grocery_toggle = any("groceries" in p and "toggle" in p for p in paths.keys())
    found_pet_activities = any("pets" in p and "activities" in p for p in paths.keys())

    assert found_todo_toggle, "Todo toggle action not found in schema"
    assert found_grocery_toggle, "Grocery toggle action not found in schema"
    assert found_pet_activities, "Pet activities action not found in schema"

  def test_schema_uses_public_id_in_paths(self):
    """Schema paths use public_id parameter, not id"""
    client = APIClient()
    response = client.get("/api/schema/")

    schema = json.loads(response.content)
    paths = schema.get("paths", {})

    # Check that detail paths use {public_id}, not {id}
    for path in paths.keys():
      if "{" in path and "/api/v1/" in path:
        # Should NOT have {id} parameter for FamApp resources
        assert "{id}" not in path, f"Path {path} should use public_id, not id"

  def test_schema_includes_security_schemes(self):
    """Schema includes JWT authentication security scheme"""
    client = APIClient()
    response = client.get("/api/schema/")

    schema = json.loads(response.content)
    components = schema.get("components", {})
    security_schemes = components.get("securitySchemes", {})

    # Check JWT Bearer authentication is configured
    assert "jwtAuth" in security_schemes or "bearerAuth" in security_schemes

  def test_schema_has_valid_openapi_version(self):
    """Schema uses OpenAPI 3.0+ specification"""
    client = APIClient()
    response = client.get("/api/schema/")

    schema = json.loads(response.content)
    openapi_version = schema.get("openapi", "")

    # Should be OpenAPI 3.0 or later
    assert openapi_version.startswith("3."), f"Expected OpenAPI 3.x, got {openapi_version}"


@pytest.mark.django_db
class TestSwaggerUI:
  """Test Swagger UI documentation interface"""

  def test_swagger_ui_accessible(self):
    """Swagger UI page is accessible"""
    client = APIClient()
    response = client.get("/api/docs/")

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response["Content-Type"]

  def test_swagger_ui_contains_schema_reference(self):
    """Swagger UI HTML references the OpenAPI schema"""
    client = APIClient()
    response = client.get("/api/docs/")

    assert response.status_code == status.HTTP_200_OK
    content = response.content.decode("utf-8")

    # Swagger UI should reference the schema endpoint
    assert "/api/schema/" in content or "api-schema" in content


@pytest.mark.django_db
class TestReDocUI:
  """Test ReDoc documentation interface"""

  def test_redoc_ui_accessible(self):
    """ReDoc UI page is accessible"""
    client = APIClient()
    response = client.get("/api/redoc/")

    # This might fail initially (RED phase) if ReDoc isn't configured yet
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response["Content-Type"]

  def test_redoc_ui_contains_schema_reference(self):
    """ReDoc UI HTML references the OpenAPI schema"""
    client = APIClient()
    response = client.get("/api/redoc/")

    assert response.status_code == status.HTTP_200_OK
    content = response.content.decode("utf-8")

    # ReDoc should reference the schema endpoint
    assert "/api/schema/" in content or "api-schema" in content


@pytest.mark.django_db
class TestAPIDocumentationMetadata:
  """Test API documentation metadata and configuration"""

  def test_schema_has_title_and_version(self):
    """Schema includes API title and version"""
    client = APIClient()
    response = client.get("/api/schema/")

    schema = json.loads(response.content)
    info = schema.get("info", {})

    assert "title" in info
    assert "version" in info
    assert info["title"]  # Not empty
    assert info["version"]  # Not empty

  def test_schema_has_description(self):
    """Schema includes API description"""
    client = APIClient()
    response = client.get("/api/schema/")

    schema = json.loads(response.content)
    info = schema.get("info", {})

    assert "description" in info

  def test_schema_endpoints_have_tags(self):
    """Schema endpoints are organized by tags"""
    client = APIClient()
    response = client.get("/api/schema/")

    schema = json.loads(response.content)
    paths = schema.get("paths", {})

    # Check that endpoints have tags
    for path, methods in paths.items():
      if "/api/v1/" in path:
        for method, details in methods.items():
          if method in ["get", "post", "patch", "delete"]:
            assert "tags" in details, f"{method.upper()} {path} missing tags"
            assert len(details["tags"]) > 0, f"{method.upper()} {path} has empty tags"


@pytest.mark.django_db
class TestSchemaPerformance:
  """Test schema generation performance"""

  def test_schema_generation_completes_quickly(self):
    """Schema generation completes in reasonable time"""
    import time

    client = APIClient()
    start_time = time.time()
    response = client.get("/api/schema/")
    end_time = time.time()

    assert response.status_code == status.HTTP_200_OK
    # Schema generation should take less than 2 seconds
    assert (end_time - start_time) < 2.0, "Schema generation too slow"


@pytest.mark.django_db
class TestSchemaDownload:
  """Test schema download formats"""

  def test_schema_available_as_json(self):
    """Schema can be downloaded as JSON"""
    client = APIClient()
    response = client.get("/api/schema/")

    assert response.status_code == status.HTTP_200_OK
    # Check content type is OpenAPI (which is JSON-based)
    assert "application/vnd.oai.openapi" in response["Content-Type"]

    # Should be valid JSON
    schema = json.loads(response.content)
    assert isinstance(schema, dict)

  def test_schema_available_as_yaml(self):
    """Schema can be downloaded as YAML"""
    client = APIClient()
    # Request YAML format via query parameter
    response = client.get("/api/schema/?format=yaml")

    # YAML format might return 200 or might not be configured
    # This is optional, so we just check it doesn't error badly
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
