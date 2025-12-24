from fastapi.testclient import TestClient

from src import app
from src.configurator import MainConfigurator

config = MainConfigurator()
base_address = config.main_api_address
api_version = '/v1'

client = TestClient(app)


def test_root():
    response = client.get(f'{base_address}/')
    assert response.status_code == 200
    assert 'welcome_text' in response.json()


def test_docs_redirect():
    response = client.get(
        f'{base_address}{api_version}/docs', follow_redirects=False
    )
    assert response.status_code == 301
    assert 'location' in response.headers


def test_redoc_redirect():
    response = client.get(
        f'{base_address}{api_version}/redoc', follow_redirects=False
    )
    assert response.status_code == 301
    assert 'location' in response.headers


def test_openapi_json_redirect():
    response = client.get(
        f'{base_address}{api_version}/openapi.json', follow_redirects=False
    )
    assert response.status_code == 301
    assert 'location' in response.headers


# def test_get_weather_found():
#     response = client.get(f'{base_address}/weather/New York')
#     assert response.status_code == 200
#     assert 'weather_name' in response.json()


# def test_get_weather_not_found():
#     response = client.get(f'{base_address}/weather/UnknownCity')
#     assert response.status_code == 400
#     assert response.json()['error'] == 'No such city'


# def test_get_query_found():
#     response = client.get(f'{base_address}/queries/1')
#     assert response.status_code == 200
#     assert 'id' in response.json()


# def test_get_query_not_found():
#     response = client.get(f'{base_address}/queries/-1')
#     assert response.status_code == 400
#     assert response.json()['error'] == 'No weather query with this ID'


# def test_get_queries_found():
#     offset = 0
#     response = client.get(
#         f'{base_address}/queries?limit=5&offset={offset}&descending=true'
#     )
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)


# def test_get_queries_not_found():
#     offset = 999999999999
#     response = client.get(
#         f'{base_address}/queries?limit=5&offset={offset}&descending=true'
#     )
#     assert response.status_code == 400
#     assert response.json()['error'] == 'End of weather queries'
