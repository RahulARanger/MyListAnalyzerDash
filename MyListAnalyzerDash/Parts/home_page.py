import typing
from dash import dcc, html, get_app
import dash_mantine_components as dmc
from MyListAnalyzerDash.utils import starry_bg
from MyListAnalyzerDash.Components.malCreds import MalCredsModal
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_row
from MyListAnalyzerDash.Components.buttons import button_with_icon
from MyListAnalyzerDash.Components.notifications import provider
from MyListAnalyzerDash.mappings.enums import main_app, home_page, mal_creds_modal


class HomePage:
    def __init__(self):
        super().__init__()
        self.mal_creds = MalCredsModal()

        self.mal_creds.init()
        self.add_routes()

    def inside_children(self):
        paper_height = 250

        labels = ["Login", "Open"]

        tab_list = dmc.TabsList(
            [dmc.Tab(_, value=_) for _ in labels]
        )

        tab_meat = [
            dmc.TabsPanel(
                dmc.Paper(
                    _, style={"height": f"{paper_height - 69}px", "background": "transparent"}, p="md"
                ),
                value=labels[index])
            for index, _ in enumerate((self.login_things(), self.show_view()))]

        tabs = dmc.Tabs([
                tab_list,
                dmc.Space(h=5),
                *tab_meat], color="orange", className="home_card", loop=True, value=labels[0],
            style=dict(
                verticalAlign="center", maxHeight=f"{paper_height}px", maxWidth="300px"
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
            className="home", loaderProps=main_app.loadingProps)

    def login_things(self):
        return expanding_layout(
            dmc.Text(home_page.greet, size="xs"),
            button_with_icon(
                "MyAnimeList", id_=mal_creds_modal.triggerId, image_src=mal_creds_modal.logo,
                size="sm"),
            spacing="xl", align="center", position="flexStart"
        )

    def connect_callbacks(self):
        ...

    def show_view(self):
        return expanding_layout(
            *(
                expanding_layout(
                    dmc.Anchor(link_text, href=href, refresh=True),
                    dmc.Text(desc, size="xs", color="orange"),
                    align="center", position="center", class_name="single_card"
                ) for link_text, href, desc in home_page.apps
            ))

    def add_routes(self):
        app = get_app()

        app.server.add_url_rule(
            self.mal_creds.route,
            view_func=self.mal_creds.tokens_to_cookies_show_2
        )
