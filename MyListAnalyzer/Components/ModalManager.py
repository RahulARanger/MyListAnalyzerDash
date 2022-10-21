from dash import ClientsideFunction, Input, Output, State, get_app, clientside_callback
import dash_mantine_components as dmc


class ModalManager:
    id_prefix = "_modal_"

    # id_prefix is the main reason why it's a class not a function
    # so don't convert it

    @classmethod
    def check(cls, clicked, opened):
        if not clicked:
            return False
        return not opened

    def __init__(self, prop_id, prop_action="n_clicks", add=False):
        self.prop_id = prop_id
        new_modal_id = ModalManager.id_prefix + self.prop_id

        if add:
            get_app().clientside_callback(
                ClientsideFunction(
                    namespace="modal",
                    function_name="decide_modal"
                ),
                Output(new_modal_id, "opened"),
                Input(prop_id, prop_action),
                # Since prop action can be different we don't have pattern matching callbacks
                State(new_modal_id, "opened")
            )

    def __call__(self, title, *children, closeable=True, ease_close=True, size="md", z_index=200):
        return dmc.Modal(
            id=ModalManager.id_prefix + self.prop_id,
            title=title, centered=True, children=children, overflow="outside", size=size,
            closeOnClickOutside=closeable and ease_close,
            closeOnEscape=closeable and ease_close, withCloseButton=closeable, zIndex=z_index
        )


def for_time(display_time_in, then="lineClamp", other=None):
    # expecting some dmc.Text for lineClamp
    return clientside_callback(
        ClientsideFunction(
            namespace="handleData",
            function_name="formatTimeInComp"
        ),
        Output(display_time_in, "children"),
        Input(display_time_in if not other else other, then)
    )
