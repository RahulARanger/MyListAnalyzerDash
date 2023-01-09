from dataclasses import dataclass
import dash_mantine_components as dmc
from dash import no_update


@dataclass
class AuthAction:
    note: dmc.Notification = no_update
    client_name: str = ""
    pic: str = no_update
    location: str = no_update
    last_update: str = 0
    trigger: str = no_update
