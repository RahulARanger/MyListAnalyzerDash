import logging
import time
import typing
from dash import no_update, html, Input, Output, State, ctx, callback, dcc
import dash_mantine_components as dmc

from MyListAnalyzerDash.mal_api_handler import VerySimpleMALSession
from MyListAnalyzerDash.Components.notifications import show_notifications
from MyListAnalyzerDash.utils import CookieHandler, get_a_proper_url, get_mapping, css_classes, get_marked
from MyListAnalyzerDash.Components.ModalManager import ModalManager, for_time
from MyListAnalyzerDash.Components.layout import expanding_layout


class CredsModal(CookieHandler):
    def __init__(self):
        super().__init__()
        self.mapping = get_mapping(self.__class__.__name__)
        self._modal = ModalManager(self.mapping.triggerId, add=True)
        self.connect_callbacks()

    def modal(self):
        body = html.Section(
            [
                expanding_layout(
                    dmc.Avatar(size="xl", radius="xl", id=self.mapping.pfp, alt="Your Pfp, if Logged in"),
                    expanding_layout(
                        dmc.TextInput(
                            id=self.mapping.client_name,
                            disabled=True, placeholder="Your Name, if logged in.",
                            required=True, style={"flexGrow": 1}
                        ),
                        dmc.Button(
                            "Login", class_name="custom-butt", id=self.mapping.login
                        ), no_wrap=True, direction="row"
                    ),
                    spacing="md", align="center", position="center"
                ),
                dmc.Space(h=6),
                dmc.Paper(
                    get_marked(self.__class__.__name__, add_limit=False)
                ),
                dmc.Space(h=10),
                expanding_layout(
                    dcc.Link(self.mapping.link_text, id=self.mapping.link_id, href=""),
                    dmc.Text(
                        self.mapping.last_prefix, id=self.mapping.last_prefix_id, size="xs", color="orange"),
                    dmc.Button(
                        "Logout",
                        id=self.mapping.logout,
                        class_name="custom-butt"
                    ), position="apart", spacing="md", align="center", direction="row", no_wrap=True
                )
            ]
        )

        return self._modal(self.mapping.title, body, ease_close=False)

    def connect_callbacks(self):
        callback(
            [
                Output(self.mapping.notify, "children"),
                Output(self.mapping.client_name, "value"),
                Output(self.mapping.pfp, "src"),
                Output(self.mapping.location, "href"),
                Output(self.mapping.last_prefix_id, "lineClamp"),
                Output(self.mapping.triggerId, "class_name")
            ],
            [
                Input(self.mapping.login, "n_clicks"),
                Input(self.mapping.logout, "n_clicks")
            ],
            State(self.mapping.location, "href")
        )(
            self.login
        )

        for_time(self.mapping.last_prefix_id)

    def login(self, login_clicked, _, location):
        # "notify", "client_name", "pfp", "location", "last_updated"
        if ctx.triggered_id == self.mapping.logout:
            return self.logout(), "", "", location, 0, css_classes.jump

        location = get_a_proper_url(location)
        return self.authenticate(location) if login_clicked else self.handle_startup(location)

    def authenticate(self, _: str):
        """
        process of verifying who a user is
        :param _:
        :return:
        """
        return no_update, no_update, no_update, _, no_update, ""

    def authorize(self, code: str, url: str) -> typing.Tuple[bool, typing.Union[str, dict]]:
        """
        process of verifying what they have access to
        :param code: code given by the Server
        :param url: redirect url
        :return:
        """
        return ...

    def check_expiry(self):
        ...

    def refresh_tokens(self):
        ...

    def handle_startup(self, location, error="", code="", key="", abt=""):
        is_error = error in self.cookies
        is_code = code in self.cookies

        if is_error:
            return show_notifications(
                "Failed to Login, please refer error below: ",
                self.cookies.pop(error)
            ), no_update, no_update, no_update, 0, css_classes.jump

        note = None

        if is_code:
            status, note = self.authorize(location, self.cookies.pop(code))
            if not status:
                return show_notifications(
                    "Failed to get tokens, please refer error below: ",
                    dmc.Code(note)
                ), no_update, no_update, no_update, 0, css_classes.jump

        return self.set_things(note, key, abt)

    def set_things(self, response, key, abt):
        logged_in = bool(response)

        if not logged_in and key in self.cookies:
            response = self.cookies / self.cookies[key]

        if logged_in:
            for check in ("client_id", "client_secret"):
                response.pop(check) if check in response else ...
            self.set_cookie_with_expiry(key, response)

        if not response:
            return show_notifications(
                f"Please login into {abt}",
                f"There's a lot you could do when logged in with your {abt} account. Here's the ",
                html.A("Reference", href=""), auto_close=3000, color="yellow"
            ), no_update, no_update, no_update, 0, css_classes.jump

        return *self.set_things_finally(response, logged_in), css_classes.customButton

    def set_things_finally(self, response, logged_in):
        try:
            formatted = float(response["asked"]) if "asked" in response else 0
        except TypeError:
            formatted = 0

        return (show_notifications(
            self.mapping.loggedIn,
            "You can now ",
            color="green",
            auto_close=2500
        ) if logged_in else no_update
                ), response.get("name", ""), response.get("picture", ""), no_update, formatted

    def logout(self, key="", abt=""):
        if key not in self.cookies:
            return show_notifications(
                "Not logged in",
                "Please sign in first 😕",
                color="violet",
                auto_close=2500
            )

        self.cookies.pop(key)
        return show_notifications(
            "Logged out",
            f"Successfully logged out from {abt}",
            auto_close=2000,
            color="green"
        )


class SimpleMALSession(CookieHandler, MALSession):
    def __init__(self):
        super().__init__()
        self.mapping = get_mapping(self.__class__.__name__)

    def validate_user(self, user_name):
        try:
            response = super().validate_user(user_name)
            assert "data" in response, "Not a valid request"
            return True, show_notifications(
                f"{user_name} is a valid user",
                f"...{user_name}", color="orange", auto_close=2500
            )
        except ConnectionRefusedError as error:
            title = "Failed to validate requested user"
            return False, show_notifications(title, str(error), auto_close=4500, color="red")

    def get_name(self):
        try:
            return super().get_name()["name"]
        except KeyError:
            return ""

    # def fetch(self):

    # try:
    #     results = self.requested_fetch(old_source, requested) if requested else self.full_fetch(old_source)
    #     self.cookies.set_expiry(key, "", self.mapping.threshold)
    # except Exception as _:
    #     logging.exception("Failed to fetch details", exc_info=True)
    #     return show_notifications(
    #         "Failed to sync with source",
    #         dmc.Text(["Error", dmc.Code(_.__class__.__name__)])
    #     ), False
    #
    # if len(results) == 0:
    #     return show_notifications(
    #         "Already Updated",
    #         "In Sync with source",
    #         color="green",
    #         auto_close=3000
    #     ), False
    #
    # return show_notifications(
    #     self.mapping.fetchedTitle,
    #     self.mapping.fetchedDesc,
    #     auto_close=2000,
    #     color="green"
    # ), results

    def is_logged_in(self):
        if self.code in self.cookies or self.error in self.cookies:
            return False
        return self.settings in self.cookies


class MALCredsModal(CredsModal, SimpleMALSession):
    def authenticate(self, location) -> str:
        return super().authenticate(MALSession.authenticate(self, location))

    def authorize(self, code, url):
        return MALSession.authorize(self, url, code)

    def handle_startup(self, location, *_):
        return super().handle_startup(location, self.error, self.code, self.settings, "MyAnimeList")

    def logout(self, *_):
        return super().logout(self.settings, "MyAnimeList")


class SimpleDriveSession(CookieHandler, GoogleDriveSession):
    def is_logged_in(self):
        if self.error in self.cookies or self.code in self.cookies:
            return False
        return self.tokens in self.cookies


class GoogleCredsModal(CredsModal, SimpleDriveSession):
    def authenticate(self, location: str):
        return super().authenticate(GoogleDriveSession.authenticate(self, location))

    def authorize(self, url, code):
        note, response = GoogleDriveSession.authorize(self, url, self.cookies / code)
        if note:
            temp = self.cookies / response
            temp["asked"] = time.time()
            name, picture = self.about_me(temp["token"])
            temp["name"] = name
            temp["picture"] = picture
        else:
            temp = response

        return note, temp

    def handle_startup(self, location, *_):
        # print(self.credentials.refresh_token)
        return super().handle_startup(location, self.error, self.code, self.tokens, "Google")

    def logout(self, *_):
        return super().logout(self.tokens, "Google")

