import dash_mantine_components as dmc
from dash import html, dcc, ctx, callback, Output, Input, State, ALL, clientside_callback, ClientsideFunction

from MyListAnalyzerDash.Components.header import ViewHeaderComponent
from MyListAnalyzerDash.Components.notifications import provider, show_notifications
from MyListAnalyzerDash.Parts.view_dashboard import ViewDashboard
from MyListAnalyzerDash.mal_api_handler import VerySimpleMALSession
from MyListAnalyzerDash.mappings.callback_proto import DataCollectionProto1
from MyListAnalyzerDash.mappings.enums import main_app, view_dashboard, view_header, mla_stores, header_menu_id
from MyListAnalyzerDash.utils import starry_bg


class ViewPage:
    def __init__(self):
        super().__init__()
        self.user_name = ""
        self.header = ViewHeaderComponent()
        self.dashboard = ViewDashboard()
        self.mal_session = VerySimpleMALSession()

    def connect_callbacks(self):
        id_, modal_id = self.header.handle_callbacks()

        clientside_callback(
            ClientsideFunction(
                function_name="validate_user",
                namespace="MLA"
            ),
            [
                Output(modal_id, "withCloseButton"),
                Output(view_dashboard.locationChange, "href"),
                Output(view_dashboard.page_settings, "data"),
                Output(modal_id, "opened"),
                Output(view_header.show_name, "children"),
                Output(view_header.show_name, "href"),
                Output(view_header.askName, "error")
            ],
            [
                Input(view_header.giveName, "n_clicks"),
                Input(view_header.askName, "debounce"),
                Input(id_, "n_clicks")
            ],
            [
                State(view_header.askName, "value"),
                State(modal_id, "opened"),
                State(view_dashboard.page_settings, "data"),
                State(view_dashboard.locationChange, "href"),
                State("pipe", "data"),
                State(view_header.giveName, "id"),
                State(view_header.askName, "id"),
                State(view_header.is_it_u, "checked")
            ]
        )

        callback(
            [
                Output(view_dashboard.startButtTrigger, "disabled"),
                Output(header_menu_id, "disabled"),
                Output(view_dashboard.intervalAsk, "max_intervals"),
                Output(view_dashboard.paging, "data"),
                Output(view_dashboard.startDetails, "children"),
                Output(view_dashboard.tempDataStore, "children"),
                Output(view_dashboard.intervalAsk, "disabled"),
                Output(header_menu_id, "color"),
                Output(view_dashboard.startButtTrigger, "color"),
                Output(view_dashboard.process_again, "size"),
                Output(dict(type=view_dashboard.tabs + self.dashboard.tab_butt, index=ALL), "disabled")
            ],
            [
                Input(view_header.show_name, "children"),
                Input(view_dashboard.startButtTrigger, "n_clicks"),
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
            dcc.Store(id=mla_stores.anime_list), dcc.Store(id=view_dashboard.paging),
            dcc.Store(id=mla_stores.recent_anime_list),
            dcc.Location(id=view_dashboard.locationChange, refresh=False), *starry_bg(),
            dmc.LoadingOverlay([
                self.header.layout(page_settings),
                dmc.ScrollArea(
                    self.dashboard.layout(page_settings),
                    type="auto", className="scroll-board"),
            ], loaderProps=main_app.loadingProps, p=0, className="home"
            ), html.Section([*self.header.modals(page_settings)], id="modals"),
            html.Aside(id=view_dashboard.tempDataStore), provider(
                view_dashboard.startDetails, view_header.resultForSearch,
                view_header.validateNote, view_dashboard.userJobDetailsNote)]

    def fetch_things(self, user_name, _, interval, temp_data, paging):
        proto = DataCollectionProto1()
        triggered = ctx.triggered_id

        proto.result = temp_data if temp_data else []
        proto.max_intervals = interval
        self.start_collecting(proto, triggered != view_dashboard.intervalAsk, user_name, paging)

        return (
            proto.disable_start, proto.disable_start, proto.max_intervals, proto.paging, proto.note,
            proto.result, proto.disable_timer,
            "grey" if proto.disable_start else "white", proto.status_color,
            proto.just_to_load_refresh, proto.disable_tabs
        )

    def start_collecting(self, proto, first_time, user_name, next_page):
        proto.max_intervals += 1

        if first_time:
            proto.note = show_notifications(
                "Starting to Fetch the Details",
                "Clearing previous data if present", color="orange", loading=True, disallowClose=True,
                force=view_dashboard.loadingNote
            )
            proto.disable_timer = False
            proto.disable_start = True
            proto.paging = ""
            proto.status_color = "gray"
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
            proto.status_color = "red"

        if _result:
            proto.result.append(build_store(_result, len(proto.result) + 1))

        if completed:
            proto.disable_start = False
            proto.disable_timer = True
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
        proto.disable_tabs = len(view_dashboard.tab_names) * [True]


def build_store(raw, index=0):
    return dcc.Store(
        data=raw, id={
            "type": view_dashboard.tempDataStore, "index": index
        }, storage_type="memory"
    )
