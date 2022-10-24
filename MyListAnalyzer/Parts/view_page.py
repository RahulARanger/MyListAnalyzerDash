from MyListAnalyzer.Components.header import ViewHeaderComponent
import dash_mantine_components as dmc
from dash import State, html, dcc, ctx
from MyListAnalyzer.mappings.enums import main_app, view_dashboard, view_header
from MyListAnalyzer.mappings.callback_proto import ValidateName
from MyListAnalyzer.Components.notifications import provider
from MyListAnalyzer.utils import starry_bg


class ViewPage:
    def __init__(self):
        self.header = ViewHeaderComponent()
        self.user_name = ""

    def connect_callbacks(self):
        self.header.handle_callbacks()

    def layout(self, user_name=""):
        return dmc.LoadingOverlay(
            [
                dcc.Store(storage_type="memory", id=view_dashboard.collectThings),
                dcc.Store(storage_type="memory", id=view_dashboard.storedName),
                dcc.Store(storage_type="memory", id=view_dashboard.userDetailsJobResult),
                dcc.Location(id=view_dashboard.locationChange, refresh=False),
                dcc.Interval(id=view_dashboard.intervalAsk, disabled=True, n_intervals=0, max_intervals=0, interval=500),
                *starry_bg(),
                dmc.Affix(self.header.layout, position={"top": 0, "left": 0}),
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



