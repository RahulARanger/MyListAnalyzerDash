import dash_mantine_components as dmc
from dash import html, dcc, Output, Input, State, clientside_callback, ClientsideFunction
from MyListAnalyzerDash.Components.header import ViewHeaderComponent
from MyListAnalyzerDash.Components.notifications import provider
from MyListAnalyzerDash.Parts.view_dashboard import ViewDashboard
from MyListAnalyzerDash.mal_api_handler import VerySimpleMALSession
from MyListAnalyzerDash.mappings.enums import main_app, view_dashboard, view_header, mla_stores
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
                function_name="validate_and_fetch_anime_list",
                namespace="MLA"
            ),
            [
                Output(modal_id, "withCloseButton"),
                Output(view_dashboard.locationChange, "href"),
                Output(view_dashboard.page_settings, "data"),
                Output(modal_id, "opened"),
                Output(view_header.show_name, "children"),
                Output(view_header.show_name, "href"),
                Output(view_header.askName, "error"),
                Output(mla_stores.tempDataStore, "data")
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
                State(view_header.is_it_u, "checked"),
                State(view_header.ask_for_nsfw, "checked"),
                State(view_header.giveName, "id"),
                State(view_header.askName, "id"),
                State(view_header.ask_for_nsfw, "id"),
                State(view_header.is_it_u, "id"),
            ]
        )
        self.dashboard.connect_callbacks()

    def layout(self, user_name="", disable_user_job=False):
        page_settings = dict(
            user_name=user_name, disable_user_job=disable_user_job
        )

        return [
            dcc.Store(id=view_dashboard.page_settings, data=page_settings),
            dcc.Store(id=mla_stores.anime_list),
            dcc.Store(id=mla_stores.recent_anime_list),
            dcc.Store(id=mla_stores.tempDataStore),
            dcc.Location(id=view_dashboard.locationChange, refresh=False), *starry_bg(),
            dmc.LoadingOverlay([
                self.header.layout(page_settings),
                dmc.ScrollArea(
                    self.dashboard.layout(page_settings),
                    type="auto", className="scroll-board"),
            ], loaderProps=main_app.loadingProps, p=0, className="home"
            ), html.Section([*self.header.modals(page_settings)], id="modals"),
            provider(view_dashboard.userJobDetailsNote)]
