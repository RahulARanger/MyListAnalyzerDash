from dash import Input, Output, clientside_callback, ClientsideFunction, dcc, State
import dash_mantine_components as dmc
from MyListAnalyzer.Components.layout import expanding_layout


def validateUser(id_, disable_id, ur_name=None, just_call=False, add=False):
    switch_id = id_ + '-name'

    if just_call:
        if not add:
            return ...

        clientside_callback(
            ClientsideFunction(namespace="eventListenerThings", function_name="invalidToDisable"),
            Output(disable_id, "disabled"),
            Input(id_, "value"),
            State(id_, "id")
        )

        clientside_callback(
            ClientsideFunction(namespace="eventListenerThings", function_name="enterToClick"),
            Output(disable_id, "id"),
            Input(id_, "n_submit"),
            [State(id_, "id"), State(disable_id, "id")],
            prevent_initial_call=True
        )

        return ...

    is_it_u = dmc.Switch(
        label='Is it you?', onLabel="yes", offLabel="no",
        size="sm", color="orange", id=switch_id, disabled=not bool(ur_name)
    )
    name = dcc.Input(
        value="", id=id_, placeholder="Enter Name!", autoFocus=True,
        pattern=r'^\w+$', required=True, className="mantine-TextInput-filledVariant mantine-TextInput-input"
    )
    action = dmc.Button("🔍", id=disable_id, color="dark", size="xs")
    return expanding_layout(name, is_it_u, action, direction="row", align="center", no_wrap=True, spacing=0)
