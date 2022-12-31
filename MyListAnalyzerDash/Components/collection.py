import typing

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, State, Output, dcc, clientside_callback, ClientsideFunction

from MyListAnalyzerDash.Components.ModalManager import get_modal, get_modal_id
from MyListAnalyzerDash.Components.graph_utils import BeautifyMyGraph, core_graph
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_row
from MyListAnalyzerDash.mappings.enums import view_header, view_dashboard, css_classes, header_menu_id


def search_user(disable_user_job=False, add=False) -> typing.Optional[
        typing.Union[typing.Tuple[dict, dict], dmc.MenuItem, dmc.Modal]]:
    if add:
        clientside_callback(
            ClientsideFunction(
                function_name="decide_if_name_required",
                namespace="MLA"
            ),
            [
                Output(view_header.askName, "disabled"),
                Output(view_header.askName, "required")
            ],
            Input(view_header.is_it_u, "checked")
        )
        return

    name_input = dmc.TextInput(
        value="", id=view_header.askName, placeholder="User Name, please",
        required=True, withAsterisk=True, rightSection=[
            dmc.ActionIcon(dmc.Image(src=view_header.addImage), id=view_header.giveName, color="dark", size="sm")
        ]
    )
    add_in_case = (dmc.Alert(
        [
            "Some Tabs are disabled because fetching user details is not required. ",
            "Please visit ", dcc.Link("view", href="/MLA/view"), " in case needed."
        ],
        title="Recent Animes are only needed", color="yellow", variant="filled"
    ),) if disable_user_job else tuple()

    return expanding_layout(
        *add_in_case,
        dmc.Alert(view_header.searchAlert, color="orange", title="Note", variant="light"),
        dmc.Space(h=10),
        name_input
    )


def filters_tab(add=False):
    if add:
        clientside_callback(
            ClientsideFunction(
                namespace="MLA",
                function_name="requestDetails"
            ),
            Output({"index": 0, "type": css_classes.request_details}, "figure"),
            Input(view_dashboard.collectThings, "data"),
            [
                State({"index": 0, "type": css_classes.request_details}, "figure"),
                State(view_dashboard.page_settings, "data")
            ]
        )
        return

    figure = BeautifyMyGraph(
        title="Requests made for User Details", x_title="Time", y_title="Time Taken(s)",
        autosize=True, show_x=True, show_y=True, show_x_grid=True, ml=3, mr=5, mb=10
    ).handle_subject(go.Figure())

    request_graph = core_graph(
        figure, responsive=True, class_name=css_classes.request_details,
        prefix=css_classes.request_details, index=0
    )
    return expanding_layout(
        dmc.Divider(color="orange"),
        request_graph,
        dmc.Divider(color="orange")
    )


def settings_tabs(add=False, disable_user_job=False):
    if add:
        return search_user(add=add), filters_tab(add)

    labels = [
        "Search User",
        "Filters"
    ]

    tab_list = dmc.TabsList(
        [dmc.Tab(_, value=_, disabled=index == 1 and disable_user_job) for index, _ in enumerate(labels)]
    )

    return dmc.Tabs([
        tab_list,
        dmc.Space(h=6),
        dmc.TabsPanel(
            search_user(disable_user_job=disable_user_job), value=labels[0]
        ),
        dmc.TabsPanel(filters_tab(), value=labels[1])
    ], color="orange", id=view_header.settingsTabs, value=labels[0])


def filters_modal(
        page_settings: typing.Optional[typing.Dict[str, typing.Union[str, bool]]] = None, add=False):
    if add:
        modal_id = get_modal_id(header_menu_id)  # filters
        settings_tabs(add=True)
        return header_menu_id, modal_id

    return get_modal(
        header_menu_id,
        expanding_row(
            dmc.Text("Search User"),
            dmc.Switch(label="For you ?", color="orange", onLabel="yes", offLabel="no", id=view_header.is_it_u),
            style=dict(alignItems="flex-end")
        ),
        search_user(), ease_close=False
    )


def fixed_menu(*options, side_ways=tuple()):
    return dmc.Affix(
        expanding_layout(
            *side_ways, dmc.Menu(
                options, trigger="click", position="top", placement="end", closeOnItemClick=True, closeOnScroll=True,
                className="corner", shadow="xl"),
            direction="row", position="center"
        ),
        position=dict(right=10, bottom=10), zIndex="2"
    )
