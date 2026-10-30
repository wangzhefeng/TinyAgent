import pytest
from mini_shop.order import (
    DEFAULT_TAX_RATE,
    discounted_total,
    total_with_tax,
)


def test_no_discount_keeps_original_total():
    assert discounted_total([100, 50], 0) == 150


def test_discount_is_subtracted_from_total():
    assert discounted_total([100, 50], 0.1) == 135


def test_default_tax_rate_is_applied():
    assert total_with_tax([100]) == 110
    assert DEFAULT_TAX_RATE == 0.1


def test_invalid_discount_is_rejected():
    with pytest.raises(ValueError):
        discounted_total([100], 0.2 + 1)
