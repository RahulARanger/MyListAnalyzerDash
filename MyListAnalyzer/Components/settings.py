import dash_mantine_components as dmc
from MyListAnalyzer.Components.ModalManager import ModalManager
from MyListAnalyzer.Components.layout import expanding_layout, expanding_scroll
from MyListAnalyzer.utils import get_mapping


class SettingsModel:
    def __init__(self, trigger, add=True):
        self.core = ModalManager(trigger, add=add)
        self.title = "Settings"
        self.search = self.__class__.__name__ + "-search"

    @property
    def body(self):
        return ...

    @property
    def inside(self):
        return expanding_scroll(
            dmc.MultiSelect(shadow="lg", label="Search", data=[], id=self.search),
            dmc.Space(h=6),
            dmc.Paper(expanding_layout(*self.body, spacing="sm"), p=0, shadow="xl")
        )

    @property
    def attach(self):
        return self.core(self.title, self.inside, closeable=True, ease_close=False)


class MyAnimeListViewSettings(SettingsModel):
    def __init__(self, *args, **__):
        super().__init__(*args, **__)
        self.mapping = get_mapping(MyAnimeListViewSettings.__name__)
        self.is_view = True

    @property
    def body(self):
        return [
            dmc.Paper(
                expanding_layout(
                    dmc.Title("Data Related", order=5),
                    dmc.Divider(color="orange"),
                    expanding_layout(
                        self.ask_first(),
                        self.ask_limit_for_fetch(), spacing="lg"
                    )
                )
            )
        ]

    def ask_first(self):
        return expanding_layout(
            dmc.Switch(
                label="Fetch Data only when asked", color="orange",
                persistence="true", persistence_type="local",
                id=self.mapping.AskToGetDataFirst
        ))

    def ask_limit_for_fetch(self):
        return expanding_layout(
            dmc.Text("Select the Limit for Each Round of the Fetch", size="xs", color="orange"),
            dmc.Slider(
                color="orange", step=100, max=1000, min=100, persistence="true", persistence_type="local",
                showLabelOnHover=True, id=self.mapping.askLimit, marks=[
                    {"value": _, "label": str(_)} for _ in range(100, 1001, 200)
                ],
            )
        )
