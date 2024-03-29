import typing
from MyListAnalyzerDash.mappings.callback_proto import AuthAction
from dash import no_update, html, Input, Output, State, ctx, callback, clientside_callback
import dash_mantine_components as dmc
from MyListAnalyzerDash.mappings.enums import mal_creds_modal, CSSClasses
from MyListAnalyzerDash.mal_api_handler import VerySimpleMALSession
from MyListAnalyzerDash.Components.notifications import show_notifications
from MyListAnalyzerDash.utils import CookieHandler, get_a_proper_url
from MyListAnalyzerDash.Components.ModalManager import make_modal_alive, get_modal, get_modal_id, relative_time_stamp_but_calc_in_good_way
from MyListAnalyzerDash.Components.layout import expanding_layout


# TODO: There's no check, if the tokens are expired or not (refresh is another task needed)
# TODO: If login failed it need not necessarily logout the existing logged in account


class MalCredsModal(CookieHandler, VerySimpleMALSession):
    @property
    def inside(self) -> html.Section:
        body = html.Section(
            [
                expanding_layout(
                    dmc.Avatar(size="xl", radius="xl", id=mal_creds_modal.pfp, alt="Your Pfp, if Logged in"),
                    dmc.Text(
                        expanding_layout(
                            "Hi,", dmc.Anchor(id=mal_creds_modal.client_name, href=""), direction="row"),
                        color="orange", size="sm"
                    ),
                    expanding_layout(
                        dmc.Button(
                            "Login", className="custom-butt", id=mal_creds_modal.login
                        ), dmc.Button(
                            "Logout",
                            id=mal_creds_modal.logout,
                            className="custom-butt"
                        ), no_wrap=True, direction="row"
                    ),
                    spacing="md", align="center", position="center"
                ),
                dmc.Space(h=20),
                dmc.Text(mal_creds_modal.access, size="sm", color="blue")
            ]
        )

        return get_modal(
            mal_creds_modal.triggerId, expanding_layout(
                mal_creds_modal.title,
                relative_time_stamp_but_calc_in_good_way(mal_creds_modal.last_prefix_id, size="xs"),
                position="apart", spacing="md", align="flex-end", direction="row",
            ), body, ease_close=False
        )

    def init(self) -> typing.NoReturn:
        make_modal_alive(mal_creds_modal.triggerId)
        callback(
            [
                Output(mal_creds_modal.notify, "children"),
                Output(mal_creds_modal.client_name, "children"),
                Output(mal_creds_modal.pfp, "src"),
                Output(mal_creds_modal.location, "href"),
                Output(mal_creds_modal.last_prefix_id, "data-time-stamp"),
                Output(mal_creds_modal.triggerId, "className")
            ],
            [
                Input(mal_creds_modal.login, "n_clicks"),
                Input(mal_creds_modal.logout, "n_clicks")
            ],
            State(mal_creds_modal.location, "href")
        )(
            self.login
        )

        relative_time_stamp_but_calc_in_good_way(
            mal_creds_modal.last_prefix_id,
            Input(get_modal_id(mal_creds_modal.triggerId), "opened"),
            add_callback=True
        )

        clientside_callback(
            """function(name){
                const redirect_to = name ? `profile/${name}` : "";
                return `https://myanimelist.net/${redirect_to}`;
            }""",
            Output(mal_creds_modal.client_name, "href"),
            Input(mal_creds_modal.client_name, "children")
        )

    def login(self, login_clicked: typing.Optional[int], _: typing.Optional[int], location: str):
        action = AuthAction()
        # "notify", "client_name", "pfp", "location", "last_updated"
        if ctx.triggered_id == mal_creds_modal.logout:
            action.note = self.logout()
            action.location = location
            action.pic = action.client_name = ""
            action.trigger = CSSClasses.jump
        else:
            location = get_a_proper_url(location)
            action.location = self.authenticate(location) if login_clicked else action.location
            self.handle_startup(location, action)

        return (
            action.note, action.client_name, action.pic, action.location, action.last_update, action.trigger
        )

    def refresh_tokens(self):
        # TODO
        ...

    def handle_startup(self, location: str, action: AuthAction):
        is_error = self.error in self.cookies
        is_code = self.code in self.cookies

        if is_error or is_code:
            action.trigger = CSSClasses.jump

        if is_error:
            action.note = show_notifications(
                "Failed to Login, please refer error below: ",
                self.cookies.pop(self.error)
            )
            return

        note = None

        if is_code:
            status, note = self.authorize(self.cookies.pop(self.code), location)
            if not status:
                action.note = show_notifications(
                    "Failed to get tokens, please refer error below: ",
                    dmc.Code(note))
                return

        return self.set_things(note, self.settings, action)

    def set_things(self, response: typing.Optional[typing.Dict[str, str]], key: str, action: AuthAction,
                   abt: str = "MyAnimeList"):
        logged_in = bool(response)

        if not logged_in and key in self.cookies:
            response = self.cookies / self.cookies[key]

        if logged_in:
            for check in ("client_id", "client_secret"):
                response.pop(check) if check in response else ...
            self.set_cookie_with_expiry(key, response, response["asked"])

        if not response:
            action.note = show_notifications(
                f"Please login into {abt}",
                f"There's a lot you could do when logged in with your {abt} account. Here's the ",
                html.A("Reference", href=""), auto_close=3000, color="yellow"
            )
            action.trigger = CSSClasses.jump
            return

        action.trigger = CSSClasses.customButton
        try:
            formatted = float(response["asked"]) if "asked" in response else 0
        except TypeError:
            formatted = 0

        action.note = show_notifications(
            mal_creds_modal.loggedIn,
            "Please refer to the", dmc.Anchor("dashboards", href=""), "for which you now have access to",
            color="green",
            auto_close=2500
        ) if logged_in else no_update

        action.client_name = response.get("name", "")
        action.pic = response.get("picture", "")
        action.last_update = formatted

    def logout(self):
        if self.settings not in self.cookies:
            return show_notifications(
                "Not logged in",
                "Please sign in first 😕",
                color="violet",
                auto_close=2500
            )

        self.cookies.pop(self.settings)
        return show_notifications(
            "Logged out",
            f"Successfully logged out from MyAnimeList",
            auto_close=2000,
            color="green"
        )
