import typing

import dash_mantine_components as dmc
from dash import dcc, Input, html

from MyListAnalyzerDash import __version__
from MyListAnalyzerDash.Components.ModalManager import timestamp_from_store, get_modal_id, make_modal_alive, get_modal
from MyListAnalyzerDash.Components.buttons import icon_butt_img
from MyListAnalyzerDash.Components.collection import filters_modal
from MyListAnalyzerDash.Components.layout import expanding_layout
from MyListAnalyzerDash.Components.table import MakeTable
from MyListAnalyzerDash.Components.tooltip import set_tooltip
from MyListAnalyzerDash.mappings.enums import view_header, header_menu_items, mla_stores, recent_anime_list


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
        ), height="35px", pl=6, pt=3, pb=3, pr=3, zIndex=1, withBorder=True,
            style=dict(backgroundColor="transparent", width="100vw"), className="view-header")


class ViewHeaderComponent(CommonHeaderComponent):
    def __init__(self):
        super().__init__()

        self.queries = view_header

    def handle_callbacks(self):
        make_modal_alive(view_header.stampsModal)
        modal_first = filters_modal(add=True)
        [timestamp_from_store(
            _, Input(get_modal_id(view_header.stampsModal), "opened"), add=True
        ) for _ in (mla_stores.anime_list, mla_stores.recent_anime_list)]

        return modal_first

    @classmethod
    def modals(cls, page_settings):
        yield filters_modal(page_settings)
        yield timestamps_modal()

    def inside_header(self, page_settings):

        user_name = page_settings.get("user_name", "")
        menu_items = [
            dmc.MenuItem(
                set_tooltip(
                    menu_item.title,
                    menu_item.desc
                ), id=menu_item.id, icon=dmc.Image(src=menu_item.image_src)
            )
            for index, menu_item in enumerate(header_menu_items)
        ]

        return dmc.Badge(
            dmc.Anchor(user_name, id=view_header.show_name, target="_blank", href="", color="orange"), color="orange"), dmc.Menu(
            [dmc.MenuTarget(
                icon_butt_img(
                    "https://api.iconify.design/line-md/close-to-menu-transition.svg?color=darkorange",
                    "_sample"
                )
            ),
                dmc.MenuDropdown(menu_items)], withArrow=True
        ),  icon_butt_img(
                    view_header.timeStamp,
                    view_header.stampsModal
                )


def header_link(title, short, url, version=__version__):
    return [
        dmc.MediaQuery(
            children=dcc.Link(
                children=html.Span(expanding_layout(
                    dmc.Title(title, order=4), html.Sup(dmc.Text(version, size="xs")),
                    direction="row", align="flex-start", position="left", spacing=1
                )),
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
                children=expanding_layout(
                    dmc.Title(short, order=5), html.Sup(dmc.Text(version, size="xs")),
                    direction="row", align="flex-start", position="left", spacing=1),
                href=url,
                className="nav_link", refresh=False
            ),
            largerThan="xs",
            styles={
                "display": "none"
            }
        )
    ]


def timestamps_modal():
    draft = MakeTable()
    draft.set_headers(("Source Name", "Time Stamp"))

    for menu_item, _id in zip(
            (header_menu_items[2], recent_anime_list),
            (mla_stores.anime_list, mla_stores.recent_anime_list)
    ):
        draft.add_cell(menu_item.title)
        draft.add_cell(timestamp_from_store(_id))
        draft.make_row()

    return get_modal(
        view_header.stampsModal,
        "Time Stamps",
        draft(),
        size="xs", opacity=1, blur=0, ease_close=False
    )
