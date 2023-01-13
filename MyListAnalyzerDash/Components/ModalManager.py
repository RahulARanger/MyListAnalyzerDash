import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, State, get_app, clientside_callback, html

from MyListAnalyzerDash.mappings.enums import css_classes


def modal_basic_check(clicked, is_opened):
    return False if not clicked else not is_opened


def get_modal_id(id_prefix):
    return id_prefix + "_modal_"


def make_modal_alive(prop_id, prop_action="n_clicks", modal_id=None, ask_first=True):
    modal_id = get_modal_id(prop_id) if not modal_id else modal_id

    get_app().clientside_callback(
        ClientsideFunction(
            namespace="modal",
            function_name="decide_modal"
        ),
        Output(modal_id, "opened"),
        Input(prop_id, prop_action),
        # Since prop action can be different we don't have pattern matching callbacks
        State(modal_id, "opened"),
        prevent_initial_call=ask_first
    )


def get_modal(id_, title, *children, closeable=True, ease_close=True, size="md", z_index=200, opacity=.69, blur=.69, opened=False):
    return dmc.Modal(
        id=get_modal_id(id_),
        title=title, centered=True, children=children, overflow="outside", size=size,
        closeOnClickOutside=closeable and ease_close, zIndex=z_index,
        closeOnEscape=closeable and ease_close, withCloseButton=closeable,
        overlayOpacity=opacity, overlayBlur=blur, overlayColor="transparent",
        opened=opened
    )


def relative_time_stamp_but_calc_in_good_way(id_, *args, add_callback=False, default="", class_name=css_classes.time_format, size="sm", isMS=False, isNotUTC=False):
    if add_callback:
        inputs = Input(id_, "data-time-stamp")

        if args:
            inputs = [inputs, *args]

        return clientside_callback(
            ClientsideFunction(
                namespace="eventListenerThings",
                function_name="formatTimeStamp"
            ),
            Output(id_, "id"),
            inputs,
            State(id_, "id"),
            prevent_initial_call=True
        )
    extras = {
        "data-time-stamp": default,
        "data-is-ms": "" if not isMS else "true",
        "data-is-not-utc": "" if not isNotUTC else "true"
    }

    extras.update(id=id_) if id_ else ...

    return dmc.Text(
        html.I(
            "Not Yet Updated", **extras,
            className=class_name
        ), size=size
    )


def timestamp_from_store(store_id, *args, class_name=css_classes.time_format, add=False):
    stamp_id = store_id + "time-stamp"
    if add:
        relative_time_stamp_but_calc_in_good_way(stamp_id, *args, add_callback=True)
        return clientside_callback(
            ClientsideFunction(
                function_name="takeThingsAndGiveThat",
                namespace="handleData"
            ),
            Output(stamp_id, "data-time-stamp"),
            Input(store_id, "modified_timestamp")
        )

    return relative_time_stamp_but_calc_in_good_way(
        stamp_id, class_name=class_name, isMS=True
    )
