import typing
from dash import dcc, html, get_app
import dash_mantine_components as dmc
from MyListAnalyzerDash.utils import starry_bg
from MyListAnalyzerDash.Components.malCreds import MalCredsModal
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_scroll
from MyListAnalyzerDash.Components.buttons import button_with_icon
from MyListAnalyzerDash.Components.notifications import provider
from MyListAnalyzerDash.mappings.enums import AppEnum, HomeEnum, mal_creds_modal


class HomePage:
    def __init__(self):
        super().__init__()
        self.mal_creds = MalCredsModal()
        self.labels = ["Login", "Open"]
        self.mal_creds.init()
        self.add_routes()

        self.paper_height = 250
        self.apps = [
            [
                "User View Dashboard", "/MLA/view/", "Dashboard for MyAnimeList Users"
            ],
            [
                "Dashboard for Recent Animes", "/MLA/view-recently/", "Dashboard for Recently Added Animes alone", True
            ],
        ]

    def inside_children(self):
        tab_list = dmc.TabsList(
            [dmc.Tab(_, value=_) for _ in self.labels]
        )

        tab_meat = [
            dmc.TabsPanel(
                dmc.Paper(
                    _, style={"height": f"{self.paper_height - 69}px", "background": "transparent"}, p="md"
                ),
                value=self.labels[index])
            for index, _ in enumerate((self.login_things(), self.show_view()))]

        tabs = dmc.Tabs([
            tab_list,
            dmc.Space(h=5),
            *tab_meat], color="orange", className="home_card", loop=True, value=self.labels[0],
            style=dict(
                verticalAlign="center", maxHeight=f"{self.paper_height}px", maxWidth="300px"
            )
        )

        return [
            *starry_bg(),
            dcc.Location(mal_creds_modal.location),
            dmc.Center(tabs, style=dict(height="100%")),
            provider(mal_creds_modal.notify),
            html.Div([self.mal_creds.inside], id="modals")
        ]

    def layout(self):
        return dmc.LoadingOverlay(
            children=self.inside_children(),
            className="home", loaderProps=AppEnum.loadingProps.value)

    def login_things(self):
        return expanding_layout(
            dmc.Text(HomeEnum.greet, size="xs"),
            button_with_icon(
                "MyAnimeList", id_=mal_creds_modal.triggerId, image_src=mal_creds_modal.logo,
                size="sm", style=dict(maxWidth="200px")), align="center", position="flexStart"
        )

    def connect_callbacks(self):
        ...

    def show_view(self):
        return dmc.Accordion(
            expanding_scroll(*(dashboard_control(*dashboard) for dashboard in self.apps), style=dict(
                height=f"{self.paper_height - 80}px"
            )),
        )

    def add_routes(self):
        app = get_app()

        app.server.add_url_rule(
            self.mal_creds.route,
            view_func=self.mal_creds.tokens_to_cookies_show_2
        )


def dashboard_control(label, url, description, mini=False):
    return dmc.AccordionItem(
        [
            dmc.AccordionControl(
                dmc.Anchor(label, href=url, size="md" if not mini else "sm", variant="gradient", refresh=True)),
            dmc.AccordionPanel(dmc.Text(description, size="sm", weight=400, color="dimmed")),
        ],
        value=label.lower()
    )
