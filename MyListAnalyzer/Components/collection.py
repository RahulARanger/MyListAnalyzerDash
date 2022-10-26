from dash import ALL, callback, Input, State, Output, no_update, dcc, clientside_callback
import dash_mantine_components as dmc
from MyListAnalyzer.mappings.enums import view_header, main_app, view_dashboard, css_classes
from MyListAnalyzer.Components.layout import expanding_layout
from MyListAnalyzer.Components.ModalManager import get_modal, make_modal_alive, get_modal_id, enter_to_click, \
    invalid_to_disable
import plotly.graph_objects as go
from MyListAnalyzer.Components.graph_utils import BeautifyMyGraph
from MyListAnalyzer.Components.cards import graph_two_cards
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
            """
            function (tabIndex, _){
                const embla_s = ["%s", ""];
                const tab_index = tabIndex || 0;
                embla_s[tab_index] && enablePlainEmbla(embla_s[tab_index]);
                return window.dash_clientside.no_update;
            }
            """ % (css_classes.request_details, ),
            Output(view_header.collectionTabs, "id"),
            [
                Input(view_header.collectionTabs, "active"),
                Input(get_modal_id(view_header.collection), "opened")
            ]
        )
        return make_modal_alive(view_header.collection)

    row_1 = expanding_layout(
        dmc.Button(
            "Start", rightIcon=[dmc.Image(src=view_dashboard.startButt)], color="dark", variant="subtle",
            id=view_dashboard.startButtTrigger),
        dmc.Badge("🤷", color="yellow", id=view_dashboard.fetchStatus),
        dmc.Button(
            "Cancel", rightIcon=[dmc.Image(src=view_dashboard.stopButt)], color="dark", variant="subtle",
            id=view_dashboard.stopButtTrigger),
        direction="row", align="center"
    )

    row_3 = expanding_layout(
        dmc.Text(
            expanding_layout(
                "Iterations Ran: ", dmc.Text("0", size="xs", id=view_dashboard.paging + "-display"),
                direction="row", align="flex-end"),
            color="violet", size="sm"),
        dmc.Text(
            expanding_layout("Last Updated at: ", dmc.Text("--"), direction="row", align="flex-end"),
            style={"fontStyle": "italic"}, color="orange", size="sm"),
        direction="row", align="center"
    )

    figure = BeautifyMyGraph().handle_subject(go.Figure())
    graph = graph_two_cards(
        figure, is_resp=True, fig_class=css_classes.request_details, class_name=css_classes.request_details)

    tab_1 = dmc.Tab(children=expanding_layout(
            row_1,
            dmc.Divider(color="orange"),
            graph,
            dmc.Divider(color="orange"),
            row_3
        ), label="User Detail")

    return get_modal(
        view_header.collection,
        "Collections 🫙",
        dmc.Tabs([tab_1], color="orange", id=view_header.collectionTabs), ease_close=False, size="lg"
    )
