import time
import requests


def refresh_token(token_url, client_id, client_secret):
    response = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    )

    response.raise_for_status()

    return response.json()["access_token"]


def fetch_all(
    url,
    token_url,
    client_id,
    client_secret,
    api_key,
    per_page=5
):
    token = refresh_token(
        token_url,
        client_id,
        client_secret
    )

    all_customers = []
    page = 1

    while True:
        headers = {
            "Authorization": f"Bearer {token}",
            "X-API-Key": api_key
        }

        response = requests.get(
            url,
            headers=headers,
            params={
                "page": page,
                "per_page": per_page
            }
        )

        if response.status_code == 401:
            token = refresh_token(
                token_url,
                client_id,
                client_secret
            )
            continue

        response.raise_for_status()

        remaining = response.headers.get(
            "X-RateLimit-Remaining"
        )

        if remaining is not None and int(remaining) == 0:
            reset = int(response.headers.get(
                "X-RateLimit-Reset", 1
            ))
            time.sleep(max(reset, 1))

        customers = response.json()["customers"]

        if not customers:
            break

        all_customers.extend(customers)
        page += 1

    return all_customers