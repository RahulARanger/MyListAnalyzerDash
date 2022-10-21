import typing
from dash import register_page, Input, Output, callback, dcc, html, clientside_callback, ClientsideFunction, State, \
    no_update, callback_context, ALL, MATCH, ctx, get_app
import dash_mantine_components as dmc
from MyListAnalyzer.utils import get_mapping, starry_bg
from MyListAnalyzer.Components.malCreds import MalCredsModal
from MyListAnalyzer.Components.layout import expanding_layout, expanding_scroll
from MyListAnalyzer.Components.buttons import icon_butt
from MyListAnalyzer.Components.ModalManager import ModalManager
from MyListAnalyzer.Components.notifications import provider
from MyListAnalyzer.mappings.enums import main_app, home_page, mal_creds_modal


class HomePage:
    def __init__(self):
        super().__init__()
        self.mal_creds = MalCredsModal()
        self.about = ModalManager(main_app.about)
        self.paper_height = 250
        self.transparent = {"backgroundColor": "transparent"}

        register_page(__name__, path=home_page.url, title=home_page.name, description=home_page.description)

        self.mal_creds.init()
        self.add_routes()

    def inside_children(self, set_active):
        tabs = dmc.Tabs(
            [
                dmc.Tab(expanding_scroll(dmc.Paper(
                    _, style={"height": f"{self.paper_height - 69}px", "background": "transparent"}, p="md")
                ), label=label) for _, label in
                ((self.login_things(), "Login"), (self.test_area(), "Tests"), (self.show_view(), "Open"))]
            , color="orange", class_name="home_card", active=set_active)

        return [
            *starry_bg(),
            dcc.Location(mal_creds_modal.location),
            dmc.Affix(
                tabs
                , position={"top": f"calc(50% - {self.paper_height // 2}px)", "left": "calc(50% - 150px)"},
                style={"width": "300px", "height": f"{self.paper_height}px"}
            ),
            provider(mal_creds_modal.notify, home_page.testNote),
            html.Div([self.mal_creds.inside], id="modals")
        ]

    def layout(self, tab):
        return dmc.MantineProvider(
            theme={"colorScheme": "dark", "fontFamily": "'segoe ui', 'Inter', sans-serif"},
            children=dmc.LoadingOverlay(
                self.inside_children(tab), id="home", loaderProps=main_app.loadingProps
            )
        )

    def login_things(self):
        return expanding_layout(
            dmc.Text(home_page.greet, size="xs"),
            icon_butt(
                "MyAnimeList", id_=mal_creds_modal.triggerId, image_src=mal_creds_modal.logo,
                size="sm"),
            # icon_butt(
            #     "Google", id_=self.google_creds.mapping.triggerId, image_src=self.google_creds.mapping.logo,
            #     size="sm", disabled=True),
            spacing="xl", align="center", position="center"
        )

    def test_area(self):
        return expanding_layout(
            expanding_layout(
                dmc.Checkbox(checked=True, label="Pass", color="green", id={
                    "type": home_page.testFilter, "index": 0}),
                dmc.Checkbox(checked=True, label="Fail", color="red", id={
                    "type": home_page.testFilter, "index": 1}),
                dmc.Checkbox(checked=True, label="Not Tested", color="yellow", id={
                    "type": home_page.testFilter, "index": 2}),
                direction="row"),
            dmc.Divider(),
            dmc.ScrollArea(
                expanding_layout(
                    id_=home_page.testResult, direction="row", spacing="sm"
                ), type="auto", style={"height": f"{self.paper_height // 2 - 30}px"}
            ),
            spacing="md"
        )

    def test_result(self, test_info, passed=None, index=0):
        return dmc.Badge(
            test_info, color="green" if passed else "red" if passed is False else "yellow", id={
                "type": home_page.testID,
                "index": index
            }, size="sm"
        )

    def connect_callbacks(self):
        # callback(
        #     Output(home_page.testResult, "children"),
        #     [
        #         Input(mal_creds_modal.client_name, "value"),
        #         Input(mal_creds_modal.notify, "children")
        #     ]
        # )(self.carry_tests)

        clientside_callback(
            ClientsideFunction(namespace="handleData", function_name="handleTests"),
            Output({"type": home_page.testID, "index": ALL}, "style"),
            Input({"type": home_page.testFilter, "index": ALL}, "checked"),
            State({"type": home_page.testID, "index": ALL}, "color")
        )

    def show_view(self):
        return expanding_layout(
            *(
                dcc.Link(
                    expanding_layout(
                        dmc.Text(link_text, color="blue", underline=True),
                        dmc.Text(desc, size="xs", color="orange"), align="center", position="center"
                    ), className="single_card", href=href, title=desc, refresh=True
                ) for link_text, href, desc in home_page.apps
            ))

    def carry_tests(self, user_name, _):
        # logged_in_mal = self.mal_creds.is_logged_in()
        #
        # check = None
        # if logged_in_mal:
        #     check = self.mal_creds.quick_test()

        test_suite = zip(
            home_page.tests,
            (logged_in_mal, True if check else None)
        )
        return [self.test_result(*_, index=index) for index, _ in enumerate(test_suite)]

    def add_routes(self):
        app = get_app()

        app.server.add_url_rule(
            self.mal_creds.route,
            view_func=self.mal_creds.tokens_to_cookies_show_2
        )
