import pprint
import typing
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, clientside_callback, ClientsideFunction, Input, Output, State, html, ALL
from MyListAnalyzer import __anime_data_source__
from MyListAnalyzer.Analyzer.graph_utils import BeautifyMyGraph
from MyListAnalyzer.Components.ModalManager import ModalManager, for_time
from MyListAnalyzer.Components.coreGraph import core_graph
from MyListAnalyzer.Components.layout import expanding_layout
from MyListAnalyzer.Components.table import table_generate
from MyListAnalyzer.utils import get_mapping, get_marked, get_profile_link
from MyListAnalyzer.Components.buttons import image_button
from MyListAnalyzer.Components.settings import MyAnimeListViewSettings
from MyListAnalyzer.Components.textinput import validateUser
from MyListAnalyzer.Analyzer.stage1_purification import request_details_for_view
from MyListAnalyzer.mappings.enums import main_page_view


def get_ends(*children, class_name="board-header"):
    return dmc.Header(
        expanding_layout(
            *children, style=False, direction="row"
        ), class_name=class_name
    )


def embed_about(_about: ModalManager, file=""):
    return _about(
        "MAL-Remainder",
        dmc.Alert(get_marked("cookieConsent"), color="orange", variant="filled"),
        (get_marked("README.md", True) if not file else get_marked(file)))


class CommonHeaderComponent:
    def __init__(self, about):
        self._mapping = get_mapping(CommonHeaderComponent.__name__)
        self.about = about
        # self._about = ModalManager(about, add=True)
        self._about = ...
        # self._changelog = ModalManager(self._mapping.changeLog)
        self._changelog = ...

        self.settings = ...
        self._collection = ...
        self.mapping = ...

    def inside_header(self):
        return ...

    def handle_callbacks(self):
        ...

    @property
    def menu_items(self) -> typing.List[typing.Union[dmc.MenuItem, dmc.MenuLabel]]:
        return [
            # dmc.Divider(label="Help", labelPosition="center"),
            # dmc.MenuItem("Docs", color="teal"),
            # dmc.MenuItem("About", id=self.about, color="orange"),
            # dmc.MenuItem("ChangeLog", id=self._mapping.changeLog, color="orange")
        ]

    @property
    def _menu(self):
        return dmc.Menu(self.menu_items)

    @property
    def layout(self):
        return dmc.Header(expanding_layout(
            *header_link(self._mapping.name, self._mapping.short_name, "/"),
            expanding_layout(
                *self.inside_header(), self._menu, spacing="sm", direction="row", align="center", position="right"
            ), direction="row"
        ))

    def modals(self):
        yield []
        ...
        # yield embed_about(self._about)


class ViewHeaderComponent(CommonHeaderComponent):

    def __init__(self, abt, is_first=True):
        super().__init__(abt)

        self.is_urs = ""
        self.mapping = get_mapping(ViewHeaderComponent.__name__)

        self._collection = ModalManager(self.mapping.collection, add=is_first)
        self._search = ModalManager(self.mapping.goToSearch, add=False)  # we have explict callback so

        self.settings = MyAnimeListViewSettings(self.mapping.settings, add=is_first)
        validateUser(self.mapping.askName, self.mapping.getName, just_call=True, add=is_first)

    def info_tab(self):
        row_1 = core_graph(
            request_details_for_view(),
            prefix=self.mapping.requestDetails, index=False, responsive=True, class_name="request-details",
            apply_shimmer=False, animate=False
        )

        return row_1

    def content(self):
        return dmc.Tabs(
            [
                dmc.Tab(self.info_tab(), label="Understood"),
                dmc.Tab(self.fetch_helper(), label="User Data"),
                dmc.Tab([], label="Recent", disabled=True)
            ], color="orange"
        )

    @property
    def menu_items(self) -> typing.List[typing.Union[dmc.MenuItem, dmc.MenuLabel]]:
        return super().menu_items + [
            dmc.MenuItem("Search a User", color="teal", id={
                "type": self.mapping.goToSearch,
                "safe": main_page_view.disableWhile
            }, icon=[dmc.Text("🔍")])
        ]

    def handle_callbacks(self):
        new_id = ModalManager.id_prefix + self.mapping.goToSearch

        clientside_callback(
            """function (enteredName){
                return Boolean(enteredName);
            }""",
            Output(new_id, "withCloseButton"),
            Input({"type": self.mapping.startFetch, "index": self.mapping.profileName}, "children")
        )

    def fetch_helper(self):
        start = dmc.Button("Start", color="orange", id={"type": self.mapping.startFetch, "index": 0})
        round_ = dmc.NumberInput(
            label="Round", description=self.mapping.roundDesc, value=0, disabled=True,
            id=self.mapping.fetchInterval)

        status_badge = dmc.Badge(id=self.mapping.jobStatus, color="gray")

        offset = dmc.NumberInput(
            label="Offset", description=self.mapping.offsetDesc, value=0, disabled=True,
            id=self.mapping.fetchOffset)

        stop = dmc.Button("Stop", color="red", id=self.mapping.stopFetch)

        row_1 = expanding_layout(
            expanding_layout(start, status_badge, stop, direction="row", align="center"),
            dmc.Divider(),
            expanding_layout(round_, offset, direction="row")
        )

        rows = [
            html.Tr([html.Td("Total Animes"),
                     html.Td("--", id={"type": self.mapping.tabular, "index": self.mapping.rowCount})]),
            html.Tr([html.Td("Last Updated at"), html.Td(dmc.Text("--", id=self.mapping.last_fetched, size="sm"))]),
            html.Tr(
                [html.Td("Genres Known"),
                 html.Td("--", id={"type": self.mapping.tabular, "index": self.mapping.genresCount})]),
            html.Tr(
                [html.Td("Studios Known"),
                 html.Td("--", id={"type": self.mapping.tabular, "index": self.mapping.studiosCount})])
        ]

        row_2 = expanding_layout(
            table_generate(self.mapping.info_table, *rows)
        )

        return expanding_layout(row_1, dmc.Divider(), row_2)

    def inside_header(self):
        return [
            dcc.Location(id=self.mapping.searchLocation),
            get_profile_link(
                self.is_urs, {"type": self.mapping.startFetch, "index": self.mapping.profileName}
            ),
            image_button(self.mapping.collectionImage, self.mapping.collection),
            image_button(self.mapping.settingsIcon, self.mapping.settings)
        ]

    def modals(self):
        yield from super().modals()
        yield self._collection(
            "Data Collection", self.content(), size="lg", ease_close=False)
        yield self.settings.attach
        yield from super().modals()
        yield self._search("Search Users", expanding_layout(
            dmc.Alert(self.mapping.note, color="red", title="Note", variant="filled"),
            validateUser(self.mapping.askName, self.mapping.getName)
        ), closeable=False)


def header_link(title, short, url):
    return [
        dmc.MediaQuery(
            dcc.Link(dmc.Title(title, order=4),
                href=url,
                className="nav_link"),
            smallerThan="xs",
            styles={"display": "none"}
        ),
        dmc.MediaQuery(
            dcc.Link(
                dmc.Title(short, order=5),
                href=url,
                className="nav_link"
            ),
            largerThan="xs",
            styles={
                "display": "none"
            }
        )
    ]
