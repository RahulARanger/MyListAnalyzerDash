import dash_mantine_components as dmc
from MyListAnalyzerDash.Components.layout import expanding_layout
import typing
from dash import dcc, clientside_callback, Input, Output
from MyListAnalyzerDash.mappings.enums import view_header
from MyListAnalyzerDash.Components.collection import settings_modal, ask_again
from MyListAnalyzerDash.Components.ModalManager import relative_time_stamp_but_calc_in_good_way, get_modal_id


class CommonHeaderComponent:
    def __init__(self):
        self.queries = ...

    def inside_header(self, *args) -> typing.Tuple[typing.Any]:
        ...

    def handle_callbacks(self):
        ...

    def layout(self, *args):
        inside_header = self.inside_header(*args)
        return dmc.Header(expanding_layout(

            *header_link(self.queries.appName, self.queries.short_name, self.queries.home),

            expanding_layout(
                *(tuple() if not inside_header else inside_header),
                spacing="sm", direction="row", align="center", position="right"
            ), direction="row"
        ))


class ViewHeaderComponent(CommonHeaderComponent):
    def __init__(self):
        super().__init__()

        self.queries = view_header

    def handle_callbacks(self):
        modal_first = settings_modal(add=True)

        relative_time_stamp_but_calc_in_good_way(
            view_header.last_updated,
            Input(view_header.settingsTabs, "active"),
            Input(get_modal_id(view_header.settings), "opened"),
            add_callback=True
        )
        return modal_first

    def inside_header(self, page_settings):
        user_name = page_settings.get("user_name", "")

        link = view_header.show_name + '-link'
        return settings_modal(page_settings), dcc.Link(
            dmc.Badge(color="orange", id=view_header.show_name, children=user_name), href="", id=link, target="_blank"
        ), settings_modal(prop=True), ask_again()


def header_link(title, short, url):
    return [
        dmc.MediaQuery(
            children=dcc.Link(
                children=dmc.Title(title, order=4),
                href=url,
                className="nav_link", refresh=False
            ),
            smallerThan="xs",
            styles={
                "display": "none"
            }
        ),
        dmc.MediaQuery(
            children=dcc.Link(
                children=dmc.Title(short, order=5),
                href=url,
                className="nav_link", refresh=False
            ),
            largerThan="xs",
            styles={
                "display": "none"
            }
        )
    ]
