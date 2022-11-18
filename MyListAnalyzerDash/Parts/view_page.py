import logging
import typing
from MyListAnalyzerDash.Components.header import ViewHeaderComponent
import dash_mantine_components as dmc
from dash import html, dcc, ctx, callback, Output, Input, State, no_update
from MyListAnalyzerDash.mappings.enums import main_app, view_dashboard, view_header
from MyListAnalyzerDash.mappings.callback_proto import ValidateName, DataCollectionProto1
from MyListAnalyzerDash.Components.notifications import provider, show_notifications
from MyListAnalyzerDash.utils import starry_bg
from MyListAnalyzerDash.mal_api_handler import VerySimpleMALSession
from MyListAnalyzerDash.Parts.view_dashboard import ViewDashboard


class ViewPage:
    def __init__(self):
        self.header = ViewHeaderComponent()
        self.user_name = ""
        self.mal_session = VerySimpleMALSession()
        self.dashboard = ViewDashboard()

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

        callback(
            [
                Output(view_dashboard.startButtTrigger, "disabled"),
                Output(view_dashboard.stopButtTrigger, "disabled"),
                Output(view_dashboard.intervalAsk, "max_intervals"),
                Output(view_dashboard.paging, "data"),
                Output(view_dashboard.startDetails, "children"),
                Output(view_dashboard.tempDataStore, "children"),
                Output(view_dashboard.intervalAsk, "disabled"),
                Output(view_dashboard.fetchStatus, "color"),
                Output(view_dashboard.fetchStatus, "children"),
                Output(view_dashboard.paging + "-display", "children"),
                Output(view_dashboard.collectThings, "data")
            ],
            [
                Input(view_header.show_name, "children"),
                Input(view_dashboard.startButtTrigger, "n_clicks"),
                Input(view_dashboard.stopButtTrigger, "n_clicks"),
                Input(view_dashboard.intervalAsk, "n_intervals")
            ],
            [
                State(view_dashboard.tempDataStore, "children"),
                State(view_dashboard.paging, "data")
            ],
            prevent_initial_call=True
        )(self.fetch_things)

        self.dashboard.connect_callbacks()

    def layout(self, user_name=""):
        return [dcc.Store(id=view_dashboard.collectThings),
                dcc.Store(id=view_dashboard.storedName),
                dcc.Store(id=view_dashboard.userDetailsJobResult),
                dcc.Store(id=view_dashboard.paging),
                dcc.Location(id=view_dashboard.locationChange, refresh=False),
                dcc.Interval(
                    id=view_dashboard.intervalAsk, disabled=True, n_intervals=0, max_intervals=0, interval=500),
                *starry_bg(),
                dmc.Affix(self.header.layout(user_name), position={"top": 0, "left": 0}),
                dmc.LoadingOverlay([
                    dmc.ScrollArea(self.dashboard.layout(), type="auto", class_name="home half-elf"),
                    dcc.Store(id={"type": view_dashboard.tabs, "index": 0}),
                    dcc.Store(id={"type": view_dashboard.tabs, "index": 1})
                ], loaderProps=main_app.loadingProps),
                html.Section(list(self.modals), id="modals"),
                html.Aside(id=view_dashboard.tempDataStore),
                provider(
                    view_dashboard.startDetails, view_header.resultForSearch,
                    view_header.validateNote, view_dashboard.userJobDetailsNote)]

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
                    logging.exception("Failed to validate a user %s", now_name, exc_info=True)

                    proto.openModal = True
                    proto.note = show_notifications(
                        f"User {now_name} does not exist",
                        f"Error Received: {_}, Please try again", color="red", auto_close=7000
                    )

        return (
            proto.note, proto.storeName, proto.openModal, proto.just_for_loading
        )

    def fetch_things(self, user_name, _, __, interval, temp_data, paging):
        proto = DataCollectionProto1()
        triggered = ctx.triggered_id

        if triggered == view_dashboard.stopButtTrigger:
            interrupt_peace(proto)
        else:
            proto.result = temp_data if temp_data else []
            proto.max_intervals = interval
            self.start_collecting(proto, triggered != view_dashboard.intervalAsk, user_name, paging)

        return (
            proto.disable_start, proto.disable_stop, proto.max_intervals, proto.paging, proto.note,
            proto.result, proto.disable_timer,
            proto.status_color, proto.status_text, len(proto.result),
            proto.perf_details
        )

    def start_collecting(self, proto, first_time, user_name, next_page):
        proto.max_intervals += 1

        if first_time:
            proto.note = show_notifications(
                "Starting to Fetch the Details",
                "Clearing previous data if present", color="orange", auto_close=2500
            )
            proto.disable_timer = proto.disable_stop = False
            proto.disable_start = True
            proto.paging = ""
            proto.status_text = "started"
            proto.status_color = "orange"
            proto.result = tuple()  # deleting previous results
            return

        limit = 1000  # limit for each round is 100 animes

        _result = None

        try:
            _result, proto.perf_details, next_page, completed = self.mal_session.peg(
                user_name, next_page=next_page, limit=limit)
            proto.paging = next_page

            if completed:
                proto.status_text = "Completed"
                proto.status_color = "green"
                proto.note = show_notifications(
                    f"Completed User Data Fetch | {user_name}",
                    "Details were fetched successfully, Please open the necessary tabs, it will plot results for you.",
                    color="teal", auto_close=4000
                )

        except Exception as _:

            proto.note = show_notifications(
                "Failed to fetch the required details",
                f"Fetch - Data Failed for the UserName: {user_name}, Reason: {_}"
            )
            completed = True
            proto.result = []  # clear prev results if failed
            proto.paging = ""
            proto.status_text = "Failed"
            proto.status_color = "red"

        if _result:
            proto.result.append(build_store(_result, len(proto.result) + 1))

        if completed:
            proto.disable_start = False
            proto.disable_timer = proto.disable_stop = True
            proto.max_intervals -= 1
            return

        proto.note = show_notifications(
            f"User Data - {user_name} - A Iteration Passed",
            "Checking if there's else more to fetch else will wrap things up",
            color="pink", auto_close=3500
        )
        proto.status_color = "orange"
        proto.status_text = "Fetching"


def interrupt_peace(return_me: DataCollectionProto1) -> typing.NoReturn:
    return_me.disable_start = False

    return_me.note = show_notifications(
        "Stopped as requested",
        view_dashboard.stop_note,
        auto_close=6900,
        color="red"
    )
    return_me.disable_timer = return_me.disable_stop = True
    return_me.status_text = "stopped"
    return_me.status_color = "red"
    return_me.paging = ""


def build_store(raw, index=0):
    return dcc.Store(
        data=raw, id={
            "type": view_dashboard.tempDataStore, "index": index
        }, storage_type="memory"
    )
