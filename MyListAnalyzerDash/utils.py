import json
import math
import pathlib
import typing
from collections import namedtuple
import datetime
import urllib.parse
from flask import request
import dash_mantine_components as dmc
from dash import callback_context, dcc, html, MATCH
from datetime import datetime, timezone

parent = pathlib.Path(__file__).parent
repo_parent_path = "https://github.com/RahulARanger/MAL-Remainder/blob/main"


def get_mapping(prefix):
    raw = json.loads((parent / "mappings" / f"{prefix}_mapping.json").read_text())
    template = namedtuple(f"{prefix}Template", raw)
    return template(**raw)


def starry_bg():
    return [html.Div(id=f"stars{_}") for _ in ("", 2, 3)]


def get_marked(prefix, force=False, add_limit=True, limit=500):
    path = (parent.parent / prefix) if force else (parent / "mappings" / f"{prefix}_marked.md")
    raw = path.read_text()

    if add_limit and len(raw) > limit:
        raw = raw[: limit] + f"... [Read More From]({repo_parent_path}/{path.relative_to(parent.parent.parent)})"

    return dcc.Markdown(raw)


def time_format():
    return datetime.now().strftime("%H:%M:%S")


def set_timestamp(title):
    return title, dmc.Text(time_format(), size="xs")


class CookieHandler:
    def __init__(self):
        super().__init__()

    def __call__(self):
        return request.cookies

    def __getitem__(self, key):
        return request.cookies.get(key)

    def __setitem__(self, key, value):
        return callback_context.response.set_cookie(key, value)

    def pop(self, key: str):
        callback_context.response.set_cookie(key, "", 0)
        return self[key]

    def __contains__(self, key):
        return key in request.cookies

    def __mul__(self, other: dict):
        return json.dumps(other)

    @property
    def cookies(self):
        return self

    def __truediv__(self, other: str) -> dict:
        return json.loads(other if other else "{}")

    def set_cookie_with_expiry(self, key, value):
        # one day before (in seconds)
        self.set_expiry(key, value, math.floor(float(value["asked"]) / 1000 - (60 * 60 * 24)))

    def set_expiry(self, key, value, expiry: int):
        callback_context.response.set_cookie(key, self.cookies * value, expiry)

    def update_cookies(self, key, new_set):
        current = self.cookies / self.cookies[key]
        current.update(new_set)
        self.cookies[key] = self.cookies * current
        return current


def get_a_proper_url(url, path="", query="", fragment=""):
    raw = urllib.parse.urlsplit(url if url else "/MLA")
    raw = raw._replace(path=path, query=query, fragment=fragment)
    new_url: str = raw.geturl()
    return new_url[: -1] if new_url.endswith("/") else new_url


def add_s(value):
    return "s" if value > 1 else ''


def format_time_delta(prefix, from_secs: float):
    return f'{prefix} {datetime.fromtimestamp(from_secs, tz=timezone.utc).strftime("%a, %b %d, %Y %I:%M")}'


def get_profile_link(name, id_):
    return dcc.Link(
        dmc.Badge("" if name else name, id=id_),
        href="" if not name else f"https://myanimelist.net/profile/{name}", target="_blank",
        style={"textDecoration": "none", "color": "white"})


def from_css(file_name, path="/MLA/assets/"):
    return html.Link(href=path + file_name, rel="stylesheet")

def genre_link(id_):
    return f"https://myanimelist.net/anime/genre/{id_}"


def studio_link(id_):
    return f"https://myanimelist.net/anime/producer/{id_}"
