import pytest
from fastapi.testclient import TestClient
from app.main import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """
    Module-scoped TestClient fixture.
    Spins up the FastAPI application once for all tests in this module,
    keeping test execution fast while still isolating HTTP concerns.
    """
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# GET / — read_root
# ---------------------------------------------------------------------------

class TestReadRoot:
    """Tests for the GET / endpoint (read_root handler)."""

    def test_returns_http_200(self, client):
        # Arrange & Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200, (
            f"Expected HTTP 200, got {response.status_code}"
        )

    def test_response_body_is_json(self, client):
        # Arrange & Act
        response = client.get("/")

        # Assert
        assert response.headers["content-type"].startswith("application/json"), (
            "Response content-type must be application/json"
        )

    def test_greeting_contains_integrion_test_optimized(self, client):
        """
        Core requirement: the root endpoint must return the updated greeting
        message that includes the string 'Integrion Test Optimized'.
        """
        # Arrange & Act
        response = client.get("/")
        body = response.json()

        # Assert – check every plausible key that a greeting could live under
        greeting_value = (
            body.get("message")
            or body.get("greeting")
            or body.get("msg")
            or ""
        )
        assert "Integrion Test Optimized" in greeting_value, (
            f"Expected 'Integrion Test Optimized' in greeting, got: {greeting_value!r}"
        )

    def test_greeting_key_exists_in_response(self, client):
        """The response body must contain at least one recognisable greeting key."""
        # Arrange & Act
        response = client.get("/")
        body = response.json()

        # Assert
        greeting_keys = {"message", "greeting", "msg"}
        assert greeting_keys & body.keys(), (
            f"None of {greeting_keys} found in response body keys: {set(body.keys())}"
        )


# ---------------------------------------------------------------------------
# POST /calculate — sum two integers
# ---------------------------------------------------------------------------

class TestCalculateEndpoint:
    """Tests for the POST /calculate endpoint."""

    # --- happy-path ---

    def test_returns_http_200_for_valid_payload(self, client):
        # Arrange
        payload = {"a": 3, "b": 7}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        assert response.status_code == 200, (
            f"Expected HTTP 200, got {response.status_code}"
        )

    def test_sum_of_two_positive_integers(self, client):
        # Arrange
        payload = {"a": 4, "b": 6}

        # Act
        response = client.post("/calculate", json=payload)
        body = response.json()

        # Assert
        assert body.get("result") == 10, (
            f"Expected result=10, got {body.get('result')!r}"
        )

    def test_sum_with_zero(self, client):
        # Arrange
        payload = {"a": 0, "b": 99}

        # Act
        response = client.post("/calculate", json=payload)
        body = response.json()

        # Assert
        assert body.get("result") == 99, (
            f"Expected result=99, got {body.get('result')!r}"
        )

    def test_sum_of_two_zeros(self, client):
        # Arrange
        payload = {"a": 0, "b": 0}

        # Act
        response = client.post("/calculate", json=payload)
        body = response.json()

        # Assert
        assert body.get("result") == 0, (
            f"Expected result=0, got {body.get('result')!r}"
        )

    def test_sum_with_negative_integers(self, client):
        # Arrange
        payload = {"a": -5, "b": 3}

        # Act
        response = client.post("/calculate", json=payload)
        body = response.json()

        # Assert
        assert body.get("result") == -2, (
            f"Expected result=-2, got {body.get('result')!r}"
        )

    def test_sum_of_two_negative_integers(self, client):
        # Arrange
        payload = {"a": -10, "b": -20}

        # Act
        response = client.post("/calculate", json=payload)
        body = response.json()

        # Assert
        assert body.get("result") == -30, (
            f"Expected result=-30, got {body.get('result')!r}"
        )

    def test_sum_of_large_integers(self, client):
        # Arrange
        payload = {"a": 1_000_000, "b": 2_000_000}

        # Act
        response = client.post("/calculate", json=payload)
        body = response.json()

        # Assert
        assert body.get("result") == 3_000_000, (
            f"Expected result=3000000, got {body.get('result')!r}"
        )

    def test_response_contains_result_key(self, client):
        """Response body must expose a 'result' key."""
        # Arrange
        payload = {"a": 1, "b": 2}

        # Act
        response = client.post("/calculate", json=payload)
        body = response.json()

        # Assert
        assert "result" in body, (
            f"'result' key missing from response body: {body}"
        )

    # --- parametrized matrix ---

    @pytest.mark.parametrize("a, b, expected", [
        (1,   1,    2),
        (10,  20,  30),
        (0,   0,    0),
        (-1,  1,    0),
        (-7, -3,  -10),
        (100, 200, 300),
    ])
    def test_sum_parametrized(self, client, a, b, expected):
        # Arrange
        payload = {"a": a, "b": b}

        # Act
        response = client.post("/calculate", json=payload)
        body = response.json()

        # Assert
        assert response.status_code == 200
        assert body.get("result") == expected, (
            f"calculate({a}, {b}): expected {expected}, got {body.get('result')!r}"
        )

    # --- error / edge cases ---

    def test_missing_field_returns_422(self, client):
        """FastAPI must reject payloads that omit a required field."""
        # Arrange – only one of the two required fields provided
        payload = {"a": 5}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        assert response.status_code == 422, (
            f"Expected HTTP 422 Unprocessable Entity, got {response.status_code}"
        )

    def test_empty_payload_returns_422(self, client):
        """FastAPI must reject completely empty payloads."""
        # Arrange & Act
        response = client.post("/calculate", json={})

        # Assert
        assert response.status_code == 422, (
            f"Expected HTTP 422 Unprocessable Entity, got {response.status_code}"
        )

    def test_non_integer_values_return_422(self, client):
        """Non-integer values must trigger FastAPI's built-in validation error."""
        # Arrange
        payload = {"a": "foo", "b": "bar"}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        assert response.status_code == 422, (
            f"Expected HTTP 422 Unprocessable Entity, got {response.status_code}"
        )
