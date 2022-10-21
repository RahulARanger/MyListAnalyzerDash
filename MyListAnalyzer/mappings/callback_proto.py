from dash import no_update
from dataclasses import dataclass
import dash_mantine_components as dmc
import typing
import plotly.graph_objects as go


# @dataclass
# class DataCollectionProto1:
#     disable_start: bool = no_update
#     disable_stop: bool = no_update
#     yes_next: int = 0
#     interval: bool = no_update
#     offset: int = no_update
#     note: dmc.Notification = no_update
#     result: typing.Dict[str, typing.Union[typing.Dict[str, str], str]] = no_update
#     timer: bool = no_update
#     details: go.Figure = no_update
#     perf: typing.Optional[typing.Dict[str, int]] = None
#     drip: typing.Optional[DataDrip] = None
#     meta: typing.Tuple[int] = (no_update,) * 3
#     implement_safe: typing.List[int] = (no_update,)
#     status_color: str = "gray"
#     status_text: str = "😴"


@dataclass
class ValidateName:
    note: typing.Optional[dmc.Notification] = no_update
    storeName: str = no_update
    openModal: str = no_update
    just_for_loading: str = no_update  # don't change this


@dataclass
class AuthAction:
    note: dmc.Notification = no_update
    client_name: str = ""
    pic: str = no_update
    location: str = no_update
    last_update: str = 0
    trigger: str = no_update
