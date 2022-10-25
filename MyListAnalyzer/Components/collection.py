import pathlib
import time
from dash import ALL, callback, Input, State, Output, no_update, dcc, clientside_callback
import dash_mantine_components as dmc
from MyListAnalyzer.mappings.enums import view_header, main_app, view_dashboard
from MyListAnalyzer.mappings.callback_proto import ValidateName
from MyListAnalyzer.Components.layout import expanding_layout
from MyListAnalyzer.Components.ModalManager import get_modal, make_modal_alive, get_modal_id, enter_to_click, \
    invalid_to_disable
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
                console.log(enteredName, "asked", Boolean(enteredName));
                return [Boolean(enteredName), enteredName, `https://myanimelist.net/profile/${enteredName}`];
            }""",

            [
                Output(modal_id, "withCloseButton"),
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
