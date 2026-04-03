"""
Integration tests for FastAPI endpoints defined in app/main.py.

Covered scenarios:
  1. GET  /          -> responds 200 with greeting 'Integrion Test Optimized'
  2. POST /calculate -> responds 200 and returns the correct sum of two integers (a + b)

All tests use FastAPI's TestClient, which spins up the ASGI app in-process
so no real network socket is opened and no external services are touched.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Module-scoped TestClient fixture.

    Using 'module' scope means the FastAPI app is initialised once for the
    entire module, which mirrors a realistic integration-test setup and keeps
    the suite fast.
    """
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# GET / — root greeting endpoint
# ---------------------------------------------------------------------------

class TestRootEndpoint:
    """Integration tests for GET /"""

    def test_root_returns_http_200(self, client: TestClient):
        """
        Arrange : TestClient is ready (provided by fixture).
        Act     : Issue a GET request to the root path.
        Assert  : HTTP status code must be 200 OK.
        """
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200, (
            f"Expected HTTP 200 but received {response.status_code}"
        )

    def test_root_returns_updated_greeting_message(self, client: TestClient):
        """
        Arrange : TestClient is ready.
        Act     : Issue a GET request to the root path.
        Assert  : Response body contains the exact updated greeting message
                  'Integrion Test Optimized'.
        """
        # Act
        response = client.get("/")

        # Assert
        body = response.json()
        assert "message" in body, (
            f"Response JSON is missing the 'message' key. Got: {body}"
        )
        assert body["message"] == "Integrion Test Optimized", (
            f"Greeting mismatch. Expected 'Integrion Test Optimized', got '{body['message']}'"
        )

    def test_root_response_is_json(self, client: TestClient):
        """
        Arrange : TestClient is ready.
        Act     : Issue a GET request to the root path.
        Assert  : Content-Type header signals JSON.
        """
        # Act
        response = client.get("/")

        # Assert
        assert "application/json" in response.headers.get("content-type", ""), (
            "Expected Content-Type to include 'application/json'"
        )


# ---------------------------------------------------------------------------
# POST /calculate — integer summation endpoint
# ---------------------------------------------------------------------------

class TestCalculateEndpoint:
    """Integration tests for POST /calculate"""

    def test_calculate_returns_http_200(self, client: TestClient):
        """
        Arrange : Provide a valid payload with two integers.
        Act     : POST the payload to /calculate.
        Assert  : HTTP status code must be 200 OK.
        """
        # Arrange
        payload = {"a": 3, "b": 7}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        assert response.status_code == 200, (
            f"Expected HTTP 200 but received {response.status_code}"
        )

    def test_calculate_returns_correct_sum_positive_integers(self, client: TestClient):
        """
        Arrange : Two positive integers whose sum is known (5 + 9 = 14).
        Act     : POST to /calculate.
        Assert  : 'result' field in response equals 14.
        """
        # Arrange
        a, b = 5, 9
        expected_sum = a + b  # 14
        payload = {"a": a, "b": b}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        body = response.json()
        assert "result" in body, (
            f"Response JSON is missing the 'result' key. Got: {body}"
        )
        assert body["result"] == expected_sum, (
            f"Sum mismatch. Expected {expected_sum}, got {body['result']}"
        )

    def test_calculate_returns_correct_sum_with_zero(self, client: TestClient):
        """
        Arrange : One operand is zero (0 + 42 = 42) — identity element edge case.
        Act     : POST to /calculate.
        Assert  : 'result' equals 42.
        """
        # Arrange
        payload = {"a": 0, "b": 42}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        body = response.json()
        assert body["result"] == 42, (
            f"Expected result 42, got {body['result']}"
        )

    def test_calculate_returns_correct_sum_negative_integers(self, client: TestClient):
        """
        Arrange : Both operands are negative (-4 + -6 = -10).
        Act     : POST to /calculate.
        Assert  : 'result' equals -10.
        """
        # Arrange
        payload = {"a": -4, "b": -6}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        body = response.json()
        assert body["result"] == -10, (
            f"Expected result -10, got {body['result']}"
        )

    def test_calculate_returns_correct_sum_mixed_sign_integers(self, client: TestClient):
        """
        Arrange : Mixed-sign operands (10 + -3 = 7).
        Act     : POST to /calculate.
        Assert  : 'result' equals 7.
        """
        # Arrange
        payload = {"a": 10, "b": -3}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        body = response.json()
        assert body["result"] == 7, (
            f"Expected result 7, got {body['result']}"
        )

    def test_calculate_response_is_json(self, client: TestClient):
        """
        Arrange : Valid payload.
        Act     : POST to /calculate.
        Assert  : Content-Type header signals JSON.
        """
        # Arrange
        payload = {"a": 1, "b": 1}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        assert "application/json" in response.headers.get("content-type", ""), (
            "Expected Content-Type to include 'application/json'"
        )

    @pytest.mark.parametrize("a, b, expected", [
        (0,   0,    0),
        (1,   1,    2),
        (100, 200,  300),
        (-50, 50,   0),
        (-1,  -1,  -2),
    ])
    def test_calculate_parametrized_sums(
        self,
        client: TestClient,
        a: int,
        b: int,
        expected: int,
    ):
        """
        Parametrized sweep: verifies a + b == expected across a representative
        range of integer pairs, including boundary and sign-variation cases.

        Arrange : Each (a, b, expected) tuple supplied by @pytest.mark.parametrize.
        Act     : POST to /calculate with the current pair.
        Assert  : 'result' matches the pre-computed expected value.
        """
        # Arrange
        payload = {"a": a, "b": b}

        # Act
        response = client.post("/calculate", json=payload)

        # Assert
        body = response.json()
        assert response.status_code == 200
        assert body["result"] == expected, (
            f"For a={a}, b={b}: expected {expected}, got {body['result']}"
        )
