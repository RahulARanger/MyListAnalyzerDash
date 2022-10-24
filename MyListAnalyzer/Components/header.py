import dash_mantine_components as dmc
from MyListAnalyzer.Components.layout import expanding_layout
import typing
from dash import dcc
from MyListAnalyzer.mappings.enums import view_header
from MyListAnalyzer.Components.collection import add_user


class CommonHeaderComponent:
    def __init__(self):
        self.queries = ...

    def inside_header(self) -> typing.Tuple[typing.Any]:
        ...

    def handle_callbacks(self):
        ...

    @property
    def menu_items(self) -> typing.List[typing.Union[dmc.MenuItem, dmc.MenuLabel]]:
        return [
            # dmc.Divider(label="Help", labelPosition="center"),
            # dmc.MenuItem("Docs", color="teal"),
            # dmc.MenuItem("About", id=self.about, color="orange"),
            # dmc.MenuItem("ChangeLog", id=self._mapping.changeLog, color="orange")
        ]

    @property
    def _menu(self):
        return dmc.Menu(self.menu_items)

    @property
    def layout(self):
        inside_header = self.inside_header()
        return dmc.Header(expanding_layout(

            *header_link(self.queries.appName, self.queries.short_name, self.queries.home),

            expanding_layout(
                *(tuple() if not inside_header else inside_header),
                self._menu, spacing="sm", direction="row", align="center", position="right"
            ), direction="row"
        ))

    def modals(self) -> typing.Sequence[dmc.Modal]:
        ...
        # yield embed_about(self._about)


class ViewHeaderComponent(CommonHeaderComponent):
    def __init__(self):
        super().__init__()

        self.queries = view_header

    @property
    def menu_items(self) -> typing.List[typing.Union[dmc.MenuItem, dmc.MenuLabel]]:
        return [
            add_user(prop=True, index=0)
        ]

    def handle_callbacks(self):
        add_user(add=True)

    @property
    def modals(self) -> typing.Sequence[dmc.Modal]:
        yield add_user()

    def inside_header(self) -> typing.Tuple[typing.Any]:
        return dmc.Badge(color="orange", children="---", id=view_header.show_name),


def header_link(title, short, url):
    return [
        dmc.MediaQuery(
            children=dcc.Link(
                children=dmc.Title(title, order=4),
                href=url,
                className="nav_link", refresh=False
            ),
            smallerThan="xs",
            styles={
                "display": "none"
            }
        ),
        dmc.MediaQuery(
            children=dcc.Link(
                children=dmc.Title(short, order=5),
                href=url,
                className="nav_link", refresh=False
            ),
            largerThan="xs",
            styles={
                "display": "none"
            }
        )
    ]
