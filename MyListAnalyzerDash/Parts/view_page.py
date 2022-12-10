import logging
import time
import typing
from MyListAnalyzerDash.Components.header import ViewHeaderComponent
import dash_mantine_components as dmc
from dash import html, dcc, ctx, callback, Output, Input, State, no_update, ALL
from MyListAnalyzerDash.mappings.enums import main_app, view_dashboard, view_header
from MyListAnalyzerDash.mappings.callback_proto import ValidateName, DataCollectionProto1
from MyListAnalyzerDash.Components.notifications import provider, show_notifications
from MyListAnalyzerDash.utils import starry_bg
from MyListAnalyzerDash.mal_api_handler import VerySimpleMALSession
from MyListAnalyzerDash.Parts.view_dashboard import ViewDashboard


class ViewPage:
    def __init__(self):
        super().__init__()
        self.user_name = ""
        self.header = ViewHeaderComponent()
        self.dashboard = ViewDashboard()
        self.mal_session = VerySimpleMALSession()

    def connect_callbacks(self):
        id_, modal_id = self.header.handle_callbacks()

        # WE use pattern matching for the id and Modal id
        # currently we only add callback (validating user) for the Index: 0

        callback(
            [
                Output(view_header.validateNote, "children"),
                Output(view_dashboard.page_settings, "data"),
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
                State(view_dashboard.page_settings, "data")
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
                Output(view_dashboard.collectThings, "data"),  # for storing the details of the requests made,
                Output(view_header.last_updated, "data-time-stamp"),
                Output(view_dashboard.process_again, "size"),
                Output(dict(type=view_dashboard.tabs + self.dashboard.tab_butt, index=ALL), "disabled")
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

    def layout(self, user_name="", disable_user_job=False):
        page_settings = dict(
            user_name=user_name, disable_user_job=disable_user_job
        )

        return [
            dcc.Interval(
                id=view_dashboard.intervalAsk, disabled=True, n_intervals=0, max_intervals=0,
                interval=500),
            dcc.Store(id=view_dashboard.collectThings),
            dcc.Store(id=view_dashboard.page_settings, data=page_settings),
            dcc.Store(id=view_dashboard.userDetailsJobResult), dcc.Store(id=view_dashboard.paging),
            dcc.Store(id=view_dashboard.recent_anime),
            dcc.Location(id=view_dashboard.locationChange, refresh=False), *starry_bg(),
            dmc.Affix(self.header.layout(page_settings), position={"top": 0, "left": 0}), dmc.LoadingOverlay([
                dmc.ScrollArea(self.dashboard.layout(page_settings), type="hover", class_name="home half-elf"),
                dcc.Store(id={"type": view_dashboard.tabs, "index": 0}),
                dcc.Store(id={"type": view_dashboard.tabs, "index": 1})
            ], loaderProps=main_app.loadingProps), html.Section(list(self.modals), id="modals"),
            html.Aside(id=view_dashboard.tempDataStore), provider(
                view_dashboard.startDetails, view_header.resultForSearch,
                view_header.validateNote, view_dashboard.userJobDetailsNote)]

    @property
    def modals(self):
        yield tuple()

    def validate(self, _, __, searched, opened, page_settings) -> typing.Tuple:
        """

        :param _: search button *click*
        :param __: asked to search button *click*
        :param searched: name that was searched in the search bar
        :param opened: Modal opened ?
        :param page_settings: page_settings
        :return: items for the DataCollectionProto1
        """
        trig = ctx.triggered_id
        _saved = page_settings.get("user_name", "").lower()
        current_name = (_saved if not (trig or searched) else searched).lower()
        already_name = "" if not trig else _saved

        action = ValidateName()
        action.openModal = True if not trig else not opened

        # if name is given or was triggered by search bar (its id is not dict type)
        while current_name or (trig and trig != view_header.settings):
            if current_name == already_name:
                break

            try:
                result = self.mal_session.validate_user(current_name)
                action.openModal = False

                action.storeName = page_settings
                action.storeName["user_name"] = current_name

                action.note = show_notifications(
                    f"User {current_name} exists",
                    f"One of the Anime from Current Watchlist: {result}",
                    color="green", auto_close=5000
                )
            except Exception as _:
                logging.exception("Failed to validate a user %s", current_name, exc_info=True)

                action.openModal = True
                action.note = show_notifications(
                    f"User {current_name} does not exist",
                    f"Error Received: {_}, Please try again", color="red", auto_close=5000
                )

            break

        return (
            action.note, action.storeName, action.openModal, action.just_for_loading
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
            proto.perf_details, time.time(), proto.just_to_load_refresh, proto.disable_tabs
        )

    def start_collecting(self, proto, first_time, user_name, next_page):
        proto.max_intervals += 1

        if first_time:
            proto.note = show_notifications(
                "Starting to Fetch the Details",
                "Clearing previous data if present", color="orange", loading=True, disallowClose=True,
                force=view_dashboard.loadingNote
            )
            proto.disable_timer = proto.disable_stop = False
            proto.disable_start = True
            proto.paging = ""
            proto.status_text = "started"
            proto.status_color = "orange"
            proto.result = tuple()  # deleting previous results
            proto.disable_tabs = len(view_dashboard.tab_names) * [True]
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
                    color="teal", action="update", force=view_dashboard.loadingNote, auto_close=3500
                )

        except Exception as _:

            proto.note = show_notifications(
                "Failed to fetch the required details",
                f"Fetch - Data Failed for the UserName: {user_name}, Reason: {_}",
                action="update", force=view_dashboard.loadingNote
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
            proto.disable_tabs = len(view_dashboard.tab_names) * [False]
            return

        proto.note = show_notifications(
            f"User Data - {user_name} - {len(proto.result)} Iteration{'s' if len(proto.result) else ''} Passed",
            "Checking if there's else more to fetch else will wrap things up",
            color="pink", loading=True, disallowClose=True,
            action="update", force=view_dashboard.loadingNote
        )
        proto.status_color = "orange"
        proto.status_text = "Fetching"
        proto.disable_tabs = len(view_dashboard.tab_names) * [True]


def interrupt_peace(return_me: DataCollectionProto1) -> typing.NoReturn:
    return_me.disable_start = False

    return_me.note = show_notifications(
        "Stopped as requested",
        view_dashboard.stop_note,
        auto_close=6900,
        color="red", loading=True, disallowClose=True,
        action="update", force=view_dashboard.loadingNote
    )
    return_me.disable_timer = return_me.disable_stop = True
    return_me.status_text = "stopped"
    return_me.status_color = "red"
    return_me.paging = ""
    return_me.disable_tabs = len(view_dashboard.tab_names) * [False]


def build_store(raw, index=0):
    return dcc.Store(
        data=raw, id={
            "type": view_dashboard.tempDataStore, "index": index
        }, storage_type="memory"
    )
