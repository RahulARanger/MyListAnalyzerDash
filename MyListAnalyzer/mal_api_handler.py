import logging
import os
import time
import requests
import typing
from flask import request, redirect, url_for, make_response
from MyListAnalyzer.utils import CookieHandler
from dataclasses import dataclass


def sanity_check(response: requests.Response):
    raw = response.json()
    if raw.get("error", ""):
        raise ConnectionRefusedError(raw.get("error"))
    response.raise_for_status()
    return raw


def abt_user(raw):
    return {"name": raw["name"], "picture": raw.get("picture", "")}


@dataclass
class AbtMAL:
    route: str = "/_mal_login"
    error: str = "error-mal"
    settings: str = "mal-creds"
    code: str = "code-mal"


class CoreMALSession(AbtMAL):
    def __init__(self):
        super().__init__()
        self.__oauth = "https://myanimelist.net/v1/oauth2"
        self.session_state = "I LOVE REM"

    @property
    def client_id(self):
        return os.getenv("MAL_CLIENT_ID")

    @classmethod
    def fake_verifier(cls):
        return "A" * 128

    def authenticate(self, url):
        return f"{self.__oauth}/authorize?response_type=code&client_id={self.client_id}&" \
               f"code_challenge={self.fake_verifier()}&" \
               f"state={self.session_state}&redirect_uri={url + self.route}"

    def tokens_to_cookies_show_2(self):
        raw = request.args

        response = make_response(redirect("/MLA"))

        if raw.get("state", "") != self.session_state or raw.get("error", ""):
            response.set_cookie(self.error, raw.get("error", "Invalid State, Request for auth failed"))
        else:
            response.set_cookie(self.code, raw.get("code", ""))

        return response

    def authorize(self, code, root_url):
        try:
            session = requests.Session()

            response = self.about_me(sanity_check(session.post(
                f"{self.__oauth}/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "code": code,
                    "code_verifier": self.fake_verifier(),
                    "redirect_uri": root_url + self.route
                }
            )), session)

            response["asked"] = time.time()
            return True, response

        except Exception as error:
            logging.exception("Failed to authorize", exc_info=True)
            return False, repr(error)

    def about_me(self, raw: typing.Dict, session: typing.Optional[requests.Session]) -> typing.Dict:
        ...


class VerySimpleMALSession(CoreMALSession):
    def __init__(self):
        self.api_url = "https://api.myanimelist.net/v2/"

        super().__init__()

    @property
    def cookies(self) -> typing.Optional[CookieHandler]:
        return ...

    def headers(self, raw=None):
        raw = raw if raw else (self.cookies / self.cookies[self.settings])
        return {"Authorization": f'{raw["token_type"]} {raw["access_token"]}'}

    @property
    def client_auth(self):
        return {"X-MAL-CLIENT-ID": self.client_id}

    def postfix(self, *then, fix="users"):
        return self.api_url + fix + "/" + "/".join(then)

    def validate_user(self, user_name):
        result = sanity_check(
            requests.get(
                self.postfix(user_name, "animelist"), headers=self.client_auth, params={
                    "offset": 0, "limit": 1, "sort": "list_updated_at"
                }))

        return "No Recent Animes found" if not result["data"] else result["data"][-1]["node"]["title"]

    def about_me(self, raw=None, session=None):
        session = session or requests.session()
        response = sanity_check(
            session.get(self.postfix("@me"), headers=self.headers(raw))
        )

        abt = abt_user(response)
        if not raw:
            return abt

        raw.update(abt)
        return raw
