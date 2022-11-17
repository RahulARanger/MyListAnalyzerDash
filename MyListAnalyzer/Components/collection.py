from dash import ALL, callback, Input, State, Output, no_update, dcc, clientside_callback, ClientsideFunction, MATCH
import dash_mantine_components as dmc
from MyListAnalyzer.mappings.enums import view_header, main_app, view_dashboard, css_classes
from MyListAnalyzer.Components.layout import expanding_layout
from MyListAnalyzer.Components.ModalManager import get_modal, make_modal_alive, get_modal_id, enter_to_click, \
    invalid_to_disable
import plotly.graph_objects as go
from MyListAnalyzer.Components.graph_utils import BeautifyMyGraph, core_graph
import typing


def add_user(index=0, prop=False, add=False) -> typing.Union[typing.Tuple[dict, dict], dmc.MenuItem, dmc.Modal]:
    id_ = {"type": view_header.getName, "index": ALL}

    if add:
        invalid_to_disable(view_header.askName, view_header.giveName)
        enter_to_click(view_header.askName, view_header.giveName)

    id_["index"] = index

    if add:
        modal_id = get_modal_id(view_header.getName)
        clientside_callback(
            """function (enteredName){
                return [
                Boolean(enteredName), `/MLA/view/${enteredName}`,
                enteredName, `https://myanimelist.net/profile/${enteredName}`
            ];
            }""",

            [
                Output(modal_id, "withCloseButton"),
                Output(view_dashboard.locationChange, "href"),
                Output(view_header.show_name, "children"),
                Output(view_header.show_name + "-link", "href"),
            ],
            Input(view_dashboard.storedName, "data")
        )

        return id_, modal_id

    if prop:
        return dmc.MenuItem("Search User 🔍", id=id_, color="teal")

    name = dcc.Input(
        value="", id=view_header.askName, placeholder="Enter Name!", autoFocus=True,
        pattern=r'^\w+$', required=True, className="mantine-TextInput-filledVariant mantine-TextInput-input"
    )

    return get_modal(
        view_header.getName, "Search User 🔍",
        expanding_layout(
            dmc.Alert("We can only search for the Public Users.", color="orange", title="Note", variant="filled"),

            expanding_layout(
                name,
                dmc.Button("+", id=view_header.giveName, color="gray", size="xs"), direction="row", align="center",
            )
        ), closeable=False
    )


def default_collections():
    return [dcc.Store(main_app.me, storage_type="memory")]


def collections(prop=False, add=False):
    if prop:
        return dmc.MenuItem(
            "Collections", color="orange", id=view_header.collection, icon=[dmc.Image(src=view_header.collectionImage)]
        )

    if add:
        clientside_callback(
            ClientsideFunction(
                namespace="MLA",
                function_name="enableEmblaForRequestDetails"
            ),
            Output(get_modal_id(view_header.collection), "id"),
            [
                Input(get_modal_id(view_header.collection), "opened"),
                Input(view_header.collectionTabs, "active")
            ]
        )

        clientside_callback(
            ClientsideFunction(
                namespace="MLA",
                function_name="requestDetails"
            ),
            Output({"index": 0, "type": css_classes.request_details}, "figure"),
            Input(view_dashboard.collectThings, "data"),
            [
                State({"index": 0, "type": css_classes.request_details}, "figure"),
                State(view_dashboard.storedName, "data")
            ]
        )

        return make_modal_alive(view_header.collection)

    row_1 = expanding_layout(
        dmc.Button(
            dmc.Image(src=view_dashboard.startButt), color="dark",
            id=view_dashboard.startButtTrigger, size="xs"),
        dmc.Badge("🤷", color="yellow", id=view_dashboard.fetchStatus),
        dmc.Button(
            dmc.Image(src=view_dashboard.stopButt), color="dark",
            id=view_dashboard.stopButtTrigger, size="xs"),
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

    tab_1 = dmc.Tab(children=expanding_layout(
        row_1,
        dmc.Divider(color="orange"),
        request_graph,
        dmc.Divider(color="orange"),
        row_3
    ), label="User Detail")

    s_row_1 = expanding_layout(
        dmc.Switch(
            label="Do not Open this Modal", offLabel="No", onLabel="Yes", color="orange",
            persistence="true", persistence_type="local", id=view_header.autoOpen
        ),
        dmc.Switch(
            label="Do not auto fetch the User Details", offLabel="No", onLabel="Yes", color="orange",
            persistence="true", persistence_type="local", id=view_header.autoRun
        ),
        direction="row"
    )

    s_row_2 = expanding_layout(
        dmc.Switch(
            label="nsfw", color="red", persistence="true", persistence_type="local",
            offLabel="🫣", onLabel="😏"
        ),
        direction="row"
    )

    settings = dmc.Paper(
        expanding_layout(
            dmc.Text("At Every Visit,", size="sm", color="orange"),
            s_row_1,
            dmc.Divider(color="orange"),
            dmc.Text("For Every Fetch,", size="sm", color="teal"),
            s_row_2,
            dmc.Divider(color="orange"),
        )
    )

    return get_modal(
        view_header.collection,
        "Collections 🫙",
        dmc.Tabs(
            [tab_1,
                dmc.Tab(settings, label="Settings")],
            color="orange", id=view_header.collectionTabs),
        ease_close=False, size="lg"
    )
