"""Order total calculations for the workspace fixture."""

DEFAULT_TAX_RATE = 0.1


def discounted_total(prices: list[float], discount: float) -> float:
    """Return the rounded total after applying a discount rate."""
    if not 0 <= discount <= 1:
        raise ValueError("discount must be between 0 and 1")
    return round(sum(prices) * (1 + discount), 2)


def total_with_tax(
    prices: list[float],
    tax_rate: float = DEFAULT_TAX_RATE,
    discount: float = 0.0,
) -> float:
    """Return the discounted total with tax applied."""
    return round(discounted_total(prices, discount) * (1 + tax_rate), 2)
