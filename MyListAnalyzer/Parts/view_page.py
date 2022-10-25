from MyListAnalyzer.Components.header import ViewHeaderComponent
import dash_mantine_components as dmc
from dash import html, dcc, ctx, callback, Output, Input, State
from MyListAnalyzer.mappings.enums import main_app, view_dashboard, view_header
from MyListAnalyzer.mappings.callback_proto import ValidateName
from MyListAnalyzer.Components.notifications import provider, show_notifications
from MyListAnalyzer.utils import starry_bg
from MyListAnalyzer.mal_api_handler import VerySimpleMALSession


class ViewPage:
    def __init__(self):
        self.header = ViewHeaderComponent()
        self.user_name = ""
        self.mal_session = VerySimpleMALSession()

    def connect_callbacks(self):
        id_, modal_id = self.header.handle_callbacks()

        # WE use pattern matching for the id and Modal id
        # currently we only add callback (validating user) for the Index: 0

        callback(
            [
                Output(view_header.validateNote, "children"),
                Output(view_dashboard.storedName, "data"),
                Output(modal_id, "opened"),
                Output(id_, "id")
            ],
            [
                Input(view_header.giveName, "n_clicks"),
                Input(id_, "n_clicks")
            ],
            [
                State(view_header.askName, "value"),
                State(modal_id, "opened"),
                State(view_dashboard.storedName, "data"),
                State(view_header.show_name, "children")
            ]
        )(self.validate)

    def layout(self, user_name=""):
        return dmc.LoadingOverlay(
            [
                dcc.Store(storage_type="memory", id=view_dashboard.collectThings),
                dcc.Store(storage_type="memory", id=view_dashboard.storedName),
                dcc.Store(storage_type="memory", id=view_dashboard.userDetailsJobResult),
                dcc.Location(id=view_dashboard.locationChange, refresh=False),
                dcc.Interval(id=view_dashboard.intervalAsk, disabled=True, n_intervals=0, max_intervals=0, interval=500),
                *starry_bg(),
                dmc.Affix(self.header.layout(user_name), position={"top": 0, "left": 0}),
                # dmc.LoadingOverlay(
                #     dmc.ScrollArea(self.dashboard.layout, type="auto", id=main_app.body),
                #     id=main_app.loadApp, loaderProps=main_app.loadingProps, style={"padding": "0px"}),
                html.Section(list(self.modals), id="modals"),
                provider(view_dashboard.startDetails, view_header.resultForSearch, view_header.validateNote),
            ],
            id="home", loaderProps=main_app.loadingProps
        )

    @property
    def modals(self):
        yield from self.header.modals

    def validate(self, _, __, name, opened, _prev, user_name):
        first_time = not _
        name = user_name if first_time and not name else name
        now_name = name.lower() if name else ""
        already_name = "" if not _prev else _prev.lower()

        trig = ctx.triggered_id

        asked_to_search = isinstance(trig, dict) and trig.get("type") == view_header.getName
        so_we_search = asked_to_search or not (now_name or _)

        proto = ValidateName()

        if so_we_search:
            proto.openModal = True if first_time else not opened
        else:
            if now_name != already_name:
                try:
                    result = self.mal_session.validate_user(now_name)
                    proto.openModal = False
                    proto.storeName = now_name
                    proto.note = show_notifications(
                        f"User {now_name} exists",
                        f"One of the Anime from Current Watchlist: {result}",
                        color="green", auto_close=5000
                    )
                except Exception as _:
                    proto.note = show_notifications(
                        f"User {user_name} does not exist",
                        f"Error Received: {_}, Please try again", color="red", auto_close=7000
                    )

        return (
            proto.note, proto.storeName, proto.openModal, proto.just_for_loading
        )




