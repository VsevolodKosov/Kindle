import re

import pytest


def _get_set_cookie_headers(response):
    return [v for (k, v) in response.headers.items() if k.lower() == "set-cookie"]


@pytest.mark.asyncio
async def test_login_register_set_cookie_attrs(client, data_user_with_password):
    reg = await client.post("/auth/register", json=data_user_with_password)
    assert reg.status_code == 201
    set_cookies = _get_set_cookie_headers(reg)
    assert any("access_token=" in sc for sc in set_cookies)
    assert any("refresh_token=" in sc for sc in set_cookies)
    for sc in set_cookies:
        assert "HttpOnly" in sc
        assert "SameSite" in sc
        assert re.search(r"Max-Age=\d+", sc)

    login = await client.post(
        "/auth/login",
        json={
            "email": data_user_with_password["email"],
            "password": data_user_with_password["password"],
        },
    )
    assert login.status_code == 200
    set_cookies_login = _get_set_cookie_headers(login)
    assert any("access_token=" in sc for sc in set_cookies_login)
    assert any("refresh_token=" in sc for sc in set_cookies_login)


@pytest.mark.asyncio
async def test_logout_deletes_cookies(client, user_with_token):
    headers = user_with_token["headers"]
    resp = await client.post("/auth/logout", headers=headers)
    assert resp.status_code == 200
    set_cookies = _get_set_cookie_headers(resp)
    assert any("access_token=" in sc for sc in set_cookies)
    assert any("refresh_token=" in sc for sc in set_cookies)
    assert any("Max-Age=0" in sc or "=;" in sc for sc in set_cookies)
