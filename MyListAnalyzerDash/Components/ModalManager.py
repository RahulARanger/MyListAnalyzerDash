import typing
from dash import ClientsideFunction, Input, Output, State, get_app, clientside_callback, html
import dash_mantine_components as dmc


def modal_basic_check(clicked, is_opened):
    return False if not clicked else not is_opened


def get_modal_id(id_prefix):
    return id_prefix + "_modal_"


def make_modal_alive(prop_id, prop_action="n_clicks", modal_id=None):
    modal_id = get_modal_id(prop_id) if not modal_id else modal_id

    get_app().clientside_callback(
        ClientsideFunction(
            namespace="modal",
            function_name="decide_modal"
        ),
        Output(modal_id, "opened"),
        Input(prop_id, prop_action),
        # Since prop action can be different we don't have pattern matching callbacks
        State(modal_id, "opened")
    )


def get_modal(id_, title, *children, closeable=True, ease_close=True, size="md", z_index=200):
    return dmc.Modal(
        id=get_modal_id(id_),
        title=title, centered=True, children=children, overflow="outside", size=size,
        closeOnClickOutside=closeable and ease_close,
        closeOnEscape=closeable and ease_close, withCloseButton=closeable, zIndex=z_index
    )


def for_time(display_time_in, then="lineClamp", other=None):
    # expecting some dmc.Text for lineClamp
    return clientside_callback(
        ClientsideFunction(
            namespace="handleData",
            function_name="formatDateTime"
        ),
        Output(display_time_in, "children"),
        Input(display_time_in if not other else other, then)
    )


def enter_to_click(text_id, button_id, action="n_submit"):
    clientside_callback(
        ClientsideFunction(
            namespace="eventListenerThings",
            function_name="enterToClick"
        ),
        Output(button_id, "id"),
        Input(text_id, action),
        [
            State(text_id, "id"),
            State(button_id, "id"),
        ]
    )


def invalid_to_disable(text_id: str, button_id: str, action: str = "value") -> typing.NoReturn:
    clientside_callback(
        ClientsideFunction(
            namespace="eventListenerThings",
            function_name="invalidToDisable"
        ),
        Output(button_id, "disabled"),
        Input(text_id, action),
        State(text_id, "id")
    )


def relative_time_stamp_but_calc_in_good_way(id_, *args, add_callback=False, default="", class_name=""):
    if add_callback:
        return clientside_callback(
            ClientsideFunction(
                namespace="eventListenerThings",
                function_name="formatTimeStamp"
            ),
            Output(id_, "id"),
            [Input(id_, "data-time-stamp"), *args],
            State(id_, "id"),
            prevent_initial_call=True
        )
    extras = {"data-time-stamp": default}
    extras.update(id=id_) if id_ else ...

    return html.I(
        "Not Yet Updated", **extras,
        className=class_name
    )
