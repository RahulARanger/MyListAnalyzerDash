from dash import Input, State, Output, dcc, clientside_callback, ClientsideFunction
import dash_mantine_components as dmc
from MyListAnalyzerDash.mappings.enums import view_header, view_dashboard, css_classes
from MyListAnalyzerDash.Components.layout import expanding_layout
from MyListAnalyzerDash.Components.ModalManager import get_modal, enter_to_click, \
    invalid_to_disable, get_modal_id
from MyListAnalyzerDash.Components.graph_utils import BeautifyMyGraph, core_graph
from MyListAnalyzerDash.Components.buttons import icon_butt_img
import plotly.graph_objects as go
import typing


def search_user_tab(disable_user_job=False, add=False) -> typing.Optional[
    typing.Union[typing.Tuple[dict, dict], dmc.MenuItem, dmc.Modal]]:
    if add:
        invalid_to_disable(view_header.askName, view_header.giveName)
        enter_to_click(view_header.askName, view_header.giveName)
        return

    name_input = dcc.Input(
        value="", id=view_header.askName, placeholder="Enter Name!", autoFocus=False,
        pattern=r'^\w+$', required=True, className="mantine-TextInput-filledVariant mantine-TextInput-input"
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
        dmc.Alert(view_header.searchAlert, color="orange", title="Note", variant="filled"),
        dmc.Space(h=10),
        expanding_layout(
            name_input,
            dmc.Button(dmc.Image(src=view_header.addImage), id=view_header.giveName, color="gray", size="xs"),
            direction="row", align="center",
        )
    )


def user_details_tab(add=False):
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

    row_1 = expanding_layout(
        dmc.Button(
            dmc.Image(src=view_dashboard.startButt), color="dark",
            id=view_dashboard.startButtTrigger, size="xs", disabled=True),
        dmc.Badge("🤷", color="yellow", id=view_dashboard.fetchStatus),
        dmc.Button(
            dmc.Image(src=view_dashboard.stopButt), color="dark",
            id=view_dashboard.stopButtTrigger, size="xs", disabled=True),
        direction="row", align="center", no_wrap=True
    )

    row_3 = expanding_layout(
        dmc.Text(
            expanding_layout(
                "Iterations Ran: ", dmc.Text("0", size="xs", id=view_dashboard.paging + "-display"),
                direction="row", align="center"),
            color="violet", size="sm"),
        dmc.Text(
            expanding_layout("Last Updated at: ", dmc.Text("--"), direction="row", align="center"),
            style={"fontStyle": "italic"}, color="orange", size="sm"),
        direction="row", align="center"
    )

    figure = BeautifyMyGraph(
        title="Requests made for User Details", x_title="Time", y_title="Time Taken(s)",
        autosize=True, show_x=True, show_y=True, show_x_grid=True, ml=3, mr=5, mb=10
    ).handle_subject(go.Figure())

    request_graph = core_graph(
        figure, responsive=True, class_name=css_classes.request_details,
        prefix=css_classes.request_details, index=0
    )
    return expanding_layout(
        row_1,
        dmc.Divider(color="orange"),
        request_graph,
        dmc.Divider(color="orange"),
        row_3
    )


def settings_tabs(add=False, disable_user_job=False):
    if add:
        return search_user_tab(add=add), user_details_tab(add)

    return dmc.Tabs(
        [dmc.Tab(
            search_user_tab(disable_user_job=disable_user_job), label="Search User 🔍"
        ),
            dmc.Tab(
                user_details_tab(),
                label="User Details", disabled=disable_user_job
            )], color="orange", id=view_header.settingsTabs
    )


def settings_modal(
        page_settings: typing.Optional[typing.Dict[str, typing.Union[str, bool]]] = None, prop=False,
        add=False):
    if add:
        modal_id = get_modal_id(view_header.settings)
        clientside_callback(
            ClientsideFunction(
                namespace="MLA",
                function_name="set_view_url_after_search"),
            [
                Output(modal_id, "withCloseButton"),
                Output(view_dashboard.locationChange, "href"),
                Output(view_header.show_name, "children"),
                Output(view_header.show_name + "-link", "href"),
            ],
            Input(view_dashboard.page_settings, "data"),
            State(view_dashboard.locationChange, "href"),
        )
        settings_tabs(add=True)
        return view_header.settings, modal_id

    if prop:
        return icon_butt_img(
            view_header.settingsImage, view_header.settings
        )

    return get_modal(
        view_header.settings,
        "Settings",
        settings_tabs(disable_user_job=page_settings.get("disable_user_job", False)), closeable=False, size="lg"
    )
