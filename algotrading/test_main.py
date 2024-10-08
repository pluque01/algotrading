from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_get_assets():
    response = client.get("/assets?search=MMM")
    assert response.status_code == 200


def test_get_strategies():
    response = client.get("/strategies")
    assert response.status_code == 200


def test_get_backtest_invalid_end_date_format():
    response = client.get(
        "/backtest?symbol=ETH&start=2022-01-01&end=2022/01/31&strategy=SmaCross"
    )
    assert response.status_code == 422
    assert response.json().get("detail") == "End date must be in the format YYYY-MM-DD"


def test_get_backtest_invalid_start_date_format():
    response = client.get(
        "/backtest?symbol=ETH&start=2022/01/01&end=2022-01-31&strategy=SmaCross"
    )
    assert response.status_code == 422
    assert (
        response.json().get("detail") == "Start date must be in the format YYYY-MM-DD"
    )


def test_get_backtest_invalid_strategy():
    response = client.get(
        "/backtest?symbol=ETH&start=2022-01-01&end=2022-01-31&strategy=InvalidStrategy"
    )
    assert response.status_code == 422
    assert response.json().get("detail") == "Strategy not found"


def test_get_backtest_invalid_timeframe():
    response = client.get(
        "/backtest?symbol=ETH&start=2022-01-01&end=2022-01-31&strategy=SmaCross&timeframe=79Minute"
    )
    assert response.status_code == 422
    assert response.json().get("detail") is not None


def test_get_backtest_no_data_found():
    response = client.get(
        "/backtest?symbol=ETH&start=2022-01-01&end=2022-01-31&strategy=SmaCross&timeframe=2Hour"
    )
    assert response.status_code == 404
    assert response.json().get("detail") == "No data found for the given input"


def test_get_backtest_successful():
    response = client.get(
        "/backtest?symbol=MMM&start=2022-01-01&end=2022-01-31&strategy=SmaCross&timeframe=2Hour"
    )
    assert response.status_code == 200
    assert response.json().get("success") is not None
