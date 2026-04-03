import pytest
from app.utils import calculate_sum, complex_logic


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_integers():
    """Provide a small set of representative integers for reuse."""
    return [0, 1, 2, 3, 5, 10]


# ---------------------------------------------------------------------------
# calculate_sum – basic addition
# ---------------------------------------------------------------------------

class TestCalculateSum:
    """Tests for the calculate_sum utility function."""

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            # (a, b, expected_sum)
            (0, 0, 0),           # identity
            (1, 2, 3),           # simple positive integers
            (-1, -2, -3),        # both negative
            (-5, 5, 0),          # cancel to zero
            (100, 200, 300),     # larger values
            (0.5, 0.5, 1.0),     # floats
            (1, -1, 0),          # mixed sign cancellation
        ],
    )
    def test_basic_addition(self, a, b, expected):
        """calculate_sum returns the correct arithmetic sum for various inputs."""
        # Arrange – inputs defined via parametrize
        # Act
        result = calculate_sum(a, b)
        # Assert
        assert result == expected

    def test_commutativity(self):
        """calculate_sum(a, b) == calculate_sum(b, a) — addition is commutative."""
        assert calculate_sum(3, 7) == calculate_sum(7, 3)

    def test_returns_numeric_type(self):
        """calculate_sum must return an int or float, not a string or None."""
        result = calculate_sum(2, 3)
        assert isinstance(result, (int, float))

    def test_sum_with_zero_identity(self):
        """Adding zero to any value must return that value unchanged."""
        assert calculate_sum(42, 0) == 42
        assert calculate_sum(0, 42) == 42


# ---------------------------------------------------------------------------
# complex_logic – quadratic operation (x ** 2)
# ---------------------------------------------------------------------------

class TestComplexLogicQuadratic:
    """
    Tests that complex_logic performs a quadratic operation (x ** 2).

    Regression guard: results must NOT match a linear formula,
    proving the old linear multiplication was replaced by x².
    """

    @pytest.mark.parametrize(
        "x, expected",
        [
            (0, 0),        # 0² = 0
            (1, 1),        # 1² = 1
            (2, 4),        # 2² = 4
            (3, 9),        # 3² = 9
            (5, 25),       # 5² = 25
            (10, 100),     # 10² = 100
            (-3, 9),       # (−3)² = 9  — negative input squares to positive
            (-7, 49),      # (−7)² = 49
        ],
    )
    def test_quadratic_output(self, x, expected):
        """complex_logic(x) must equal x squared for all representative inputs."""
        # Arrange – x and expected provided by parametrize
        # Act
        result = complex_logic(x)
        # Assert
        assert result == expected, (
            f"Expected complex_logic({x}) == {x}**2 == {expected}, got {result}"
        )

    def test_quadratic_not_linear(self):
        """
        Regression guard: ensure the result is NOT linear (x * constant).
        For x=3, any linear formula k*x with k>1 would differ from x²=9
        only when x != k.  We use x=4: 4²=16.  A former linear factor of e.g.
        2 would give 8, 3 would give 12 – none equal 16.
        """
        x = 4
        quadratic_expected = x ** 2   # 16
        result = complex_logic(x)

        assert result == quadratic_expected, (
            f"complex_logic({x}) should be {quadratic_expected} (quadratic), got {result}"
        )
        # Explicitly assert it is NOT a simple linear multiple (2x or 3x)
        assert result != 2 * x, "complex_logic must not behave as 2x (linear)"
        assert result != 3 * x, "complex_logic must not behave as 3x (linear)"

    def test_symmetry_of_squared_negatives(self):
        """complex_logic(-x) must equal complex_logic(x) because (−x)²=x²."""
        for x in [1, 2, 5, 7, 11]:
            assert complex_logic(-x) == complex_logic(x), (
                f"Symmetry broken: complex_logic(-{x}) != complex_logic({x})"
            )

    def test_monotonically_increasing_for_positive_inputs(self, small_integers):
        """
        For positive x, x² is strictly increasing.
        Verifies the quadratic growth shape rather than a flat/linear trend.
        """
        positive = [x for x in small_integers if x > 0]
        results = [complex_logic(x) for x in positive]
        for i in range(len(results) - 1):
            assert results[i] < results[i + 1], (
                f"Expected strictly increasing quadratic output but "
                f"complex_logic({positive[i]})={results[i]} >= "
                f"complex_logic({positive[i+1]})={results[i+1]}"
            )

    def test_zero_input_returns_zero(self):
        """complex_logic(0) must return 0 because 0²=0."""
        assert complex_logic(0) == 0

    def test_large_value_quadratic(self):
        """Spot-check a large value to confirm quadratic scaling holds."""
        x = 50
        assert complex_logic(x) == x ** 2  # 2500
