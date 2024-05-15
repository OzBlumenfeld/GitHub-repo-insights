import requests


def _get_request(url: str, headers: dict) -> requests.Response:
    return requests.get(url=url, headers=headers)
