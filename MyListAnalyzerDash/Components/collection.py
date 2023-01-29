import typing
import dash_mantine_components as dmc
from dash import Input, Output, clientside_callback, ClientsideFunction
from MyListAnalyzerDash.Components.ModalManager import get_modal, get_modal_id
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_row
from MyListAnalyzerDash.Components.tooltip import set_tooltip
from MyListAnalyzerDash.mappings.enums import view_header, header_menu_id


def search_user(default_user_name="", disable_user_job=False, add=False):
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

    nsfw = dmc.Switch(
        label="nsfw", color="red", onLabel="yes", offLabel="no", id=view_header.ask_for_nsfw, disabled=disable_user_job)

    nsfw_switch = nsfw if not disable_user_job else set_tooltip(
        nsfw, label="You do not need this filter now"
    )

    name_input = dmc.TextInput(
        value=default_user_name, id=view_header.askName, placeholder="User Name, please",
        required=True, withAsterisk=True, rightSection=[
            dmc.ActionIcon(dmc.Image(src=view_header.addImage), id=view_header.giveName, color="dark", size="sm")
        ], style=dict(flexGrow=1)
    )

    return expanding_layout(
        dmc.Alert(view_header.searchAlert, color="orange", title="Note", variant="light"),
        dmc.Space(h=10),
        expanding_layout(name_input, nsfw_switch)
    )


def search_user_modal(
        page_settings: typing.Optional[typing.Dict[str, typing.Union[str, bool]]] = None, add=False):
    if add:
        modal_id = get_modal_id(header_menu_id)  # filters
        search_user(add=True)
        return header_menu_id, modal_id

    disable = page_settings["disable_user_job"]

    return get_modal(
        header_menu_id,
        expanding_layout(
            dmc.Text("Search User", style=dict(flexGrow=1)),
            dmc.Switch(label="For you ?", color="orange", onLabel="yes", offLabel="no", id=view_header.is_it_u),
            direction="row", no_wrap=True, align="flex-end"
        ),
        search_user(page_settings["user_name"], disable), ease_close=False, opened=True
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
