import pathlib
import time
from dash import ALL, callback, Input, State, Output, no_update, dcc, clientside_callback
import dash_mantine_components as dmc
from MyListAnalyzer.Components.buttons import image_button
from MyListAnalyzer.mappings.enums import view_header, main_app, view_dashboard
from MyListAnalyzer.Components.layout import expanding_layout
from MyListAnalyzer.Components.ModalManager import get_modal, make_modal_alive, get_modal_id, enter_to_click, \
    invalid_to_disable


def add_user(index=0, prop=False, add=False):
    id_ = {"type": view_header.getName, "index": ALL}

    if add:
        # callback(
        #     Output(view_header.giveName, "style"),
        #     Input(view_header.giveName, "n_clicks"),
        #     State(view_header.askName, "value")
        # )(validate_user)
        # callback(
        #     Input()
        # )

        modal_id = get_modal_id(view_header.getName)

        clientside_callback(
            (pathlib.Path(__file__).parent.parent / "scripts" / "validateUser.js").read_text(),
            [
                Output(view_dashboard.storedName, "data"),
                Output(modal_id, "opened"),
                Output(view_header.validateNote, "children")
            ],
            [
                Input(view_header.giveName, "n_clicks"),
                Input(id_, "n_clicks")
            ],
            [
                State(view_header.askName, "value"),
                State(modal_id, "opened"),
                State(view_dashboard.storedName, "data"),
                State(view_header.show_name, "children"),
                State("pipe", "data")
            ]

        )

        invalid_to_disable(view_header.askName, view_header.giveName)

        # clientside_callback(
        #     """function (enteredName){
        #         return Boolean(enteredName);
        #     }""",
        #     Output(new_id, "withCloseButton"),
        #     Input({"type": self.mapping.startFetch, "index": self.mapping.profileName}, "children")
        # )

        enter_to_click(view_header.askName, view_header.giveName)
        return

        # return make_modal_alive(id_, modal_id=get_modal_id(view_header.getName))

    id_["index"] = index

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
        ), ease_close=False
    )


def validate_user(clicked, entered):
    if not clicked:
        return no_update
    return no_update


def default_collections():
    return [dcc.Store(main_app.me, storage_type="memory")]
