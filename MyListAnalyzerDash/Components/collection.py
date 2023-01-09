import typing
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, dcc, clientside_callback, ClientsideFunction
from MyListAnalyzerDash.Components.ModalManager import get_modal, get_modal_id
from MyListAnalyzerDash.Components.graph_utils import BeautifyMyGraph, core_graph
from MyListAnalyzerDash.Components.layout import expanding_layout
from MyListAnalyzerDash.mappings.enums import view_header, css_classes, header_menu_id


def search_user(default_user_name="", disable_user_job=False, add=False) -> typing.Optional[
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
        value=default_user_name, id=view_header.askName, placeholder="User Name, please",
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


def settings_tabs(page_settings, add=False):
    if add:
        return search_user(add=add), filters_tab(add)

    labels = [
        "Search User",
        "Filters"
    ]

    tab_list = dmc.TabsList(
        [dmc.Tab(_, value=_, disabled=index == 1) for index, _ in enumerate(labels)]
    )

    return dmc.Tabs([
        tab_list,
        dmc.Space(h=6),
        dmc.TabsPanel(
            search_user(page_settings.get("user_name", "")), value=labels[0]
        ),
        dmc.TabsPanel(filters_tab(), value=labels[1])
    ], color="orange", id=view_header.settingsTabs, value=labels[0])


def filters_modal(
        page_settings: typing.Optional[typing.Dict[str, typing.Union[str, bool]]] = None, add=False):
    if add:
        modal_id = get_modal_id(header_menu_id)  # filters
        settings_tabs(page_settings, add=True)
        return header_menu_id, modal_id

    return get_modal(
        header_menu_id,
        expanding_layout(
            dmc.Text("Search User"),
            dmc.Switch(label="For you ?", color="orange", onLabel="yes", offLabel="no", id=view_header.is_it_u),
            direction="row", no_wrap=True, align="flex-end"
        ),
        search_user(page_settings["user_name"], page_settings["disable_user_job"]), ease_close=False, opened=True
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
