"""Tests for stock_checker module."""

from unittest.mock import patch, MagicMock


@patch("src.stock_checker._cache")
def test_check_stock_returns_zero_on_miss(mock_cache):
    mock_cache.get.return_value = None
    from src.stock_checker import check_stock
    assert check_stock("GRO-441") == 0


@patch("src.stock_checker._cache")
def test_check_stock_returns_int(mock_cache):
    mock_cache.get.return_value = "47"
    from src.stock_checker import check_stock
    assert check_stock("GRO-441") == 47


@patch("src.stock_checker.check_stock")
def test_is_available_false_when_zero(mock_check):
    mock_check.return_value = 0
    from src.stock_checker import is_available
    assert is_available("GRO-441", 1) is False


@patch("src.stock_checker.check_stock")
def test_is_available_true_when_sufficient(mock_check):
    mock_check.return_value = 10
    from src.stock_checker import is_available
    assert is_available("GRO-441", 5) is True
