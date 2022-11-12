from dash import dcc, callback, Output, State, Input, MATCH, no_update, clientside_callback, ClientsideFunction, ALL, \
    html
import dash_mantine_components as dmc
from MyListAnalyzer.mappings.enums import view_dashboard, status_colors, status_labels
from MyListAnalyzer.Components.cards import number_card_format_1, no_data, error_card, graph_two_cards, core_graph
from MyListAnalyzer.Components.layout import expanding_row, expanding_layout, expanding_scroll
from MyListAnalyzer.Components.notifications import show_notifications
from MyListAnalyzer.Components.graph_utils import BeautifyMyGraph
import json
import plotly.graph_objects as go


class ViewDashboard:
    def __init__(self):
        self.postfix_tab = "-tab"

    def connect_callbacks(self):
        postfix_tab = view_dashboard.tabs + self.postfix_tab
        callback(
            Output(dict(type=postfix_tab, index=view_dashboard.tab_names[0]), "children"),
            Input(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[0]), "data")
        )(self.process_tabs)

        clientside_callback(
            ClientsideFunction(
                namespace="MLA",
                function_name="refreshTab"
            ),
            Output(dict(type=postfix_tab, index=MATCH), "id"),
            Input(dict(type=postfix_tab, index=MATCH), "children"),
            State(dict(type=postfix_tab, index=MATCH), "id")
        )  # this happens when data is changed

        clientside_callback(
            ClientsideFunction(
                namespace="MLA",
                function_name="processUserDetailsWhenNeeded"
            ),
            [
                Output(dict(type=view_dashboard.tabs, index=ALL), "data"),
                Output(view_dashboard.userJobDetailsNote, "children"),
                Output(view_dashboard.userDetailsJobResult, "data")
            ],
            [
                Input(view_dashboard.intervalAsk, "disabled"),
                Input(view_dashboard.tabs, "active"),
            ],
            [
                State(view_dashboard.fetchStatus, "color"),
                State(view_dashboard.userDetailsJobResult, "data"),
                State(dict(type=view_dashboard.tempDataStore, index=ALL), "data"),
                State("pipe", "data"),
                State(view_dashboard.storedName, "data"),
                State(dict(type=view_dashboard.tabs, index=ALL), "data"),
                State(dict(type=postfix_tab, index=ALL), "id"),
            ]
        )

    def layout(self):
        postfix_tab = view_dashboard.tabs + self.postfix_tab

        tabs = []
        store = []

        for index, label in enumerate(view_dashboard.tab_names):
            tabs.append(dmc.Tab(
                children=dmc.Skeleton(dmc.Paper(
                    no_data("Please wait until results are fetched", force=True),
                    pl=10, pr=10, pb=10,
                    id=dict(type=postfix_tab, index=label), style={"backgroundColor": "transparent"}),
                    visible=False, animate=True), label=label, disabled=index == 1))
            store.append(
                dcc.Store(storage_type="memory", id=dict(type=view_dashboard.tabs, index=label), data=""))

        return html.Section([
            dmc.Tabs(
                children=tabs, color="orange",
                style={"fontSize": "0.5rem"}, id=view_dashboard.tabs, persistence="true",
                persistence_type="memory"),
            *store
        ])

    def process_tabs(self, data):
        print(data)
        if not data:
            return no_data("Collections -> user details")

        graph_class = view_dashboard.tab_names[0] + "-graphs"

        try:
            row_1, row_2, histogram_plot, (season, this_year), wht_the_dog_dng = process_overview(data)
        except Exception as error:
            return error_card("Failed to plot results: %s, Might be server returned invalid results" % (repr(error),))

        first_row = expanding_row(*(
            number_card_format_1(
                number=value, label=label,
                color=color, class_name=view_dashboard.tab_names[0], is_percent=False)
            for value, label, color in row_1
        ))

        second_row = expanding_row(*(
            number_card_format_1(
                number=value, is_percent=True, label=label.capitalize(),
                class_name=view_dashboard.tab_names[0], another=exact,
                color=color
            ) for label, (exact, value), color in row_2
        ))

        ep_range = core_graph(
            histogram_plot,
            apply_shimmer=False, index=1, prefix=view_dashboard.tab_names[0], class_name=graph_class,
            responsive=True
        )

        wht_dng = core_graph(
            wht_the_dog_dng,
            apply_shimmer=False, index=2, prefix=view_dashboard.tab_names[0], class_name=graph_class,
            responsive=True
        )

        this_year_season = core_graph(
            season if not this_year else this_year,
            prefix=view_dashboard.tab_names[0],
            apply_shimmer=False,
            index=2,
            responsive=True,
            class_name=graph_class
        )

        seasons_plot = graph_two_cards(
            season, class_name=view_dashboard.tab_names[0], animate=False,
            fig_class=graph_class, is_resp=True, index=3, second_card=this_year_season
        ) if season and this_year else this_year_season

        third_row = expanding_row(
            ep_range, seasons_plot, wht_dng
        )

        return expanding_scroll(*[
            __ for _ in (first_row, second_row, third_row) for __ in
            [_, dmc.Divider(color="dark", style={"opacity": 0.5, "marginBottom": "2px"})]
        ])


def process_overview(data):
    row_1 = data["row_1"]
    row_2 = json.loads(data["row_2"])
    row_3 = data["row_3"]

    yield zip(row_1["values"], row_1["keys"], view_dashboard.row_1_colors)
    yield zip(
        map(lambda x: getattr(status_labels, x), row_2["index"]),
        row_2["data"], map(lambda x: getattr(status_colors, x), row_2["index"])
    )

    yield BeautifyMyGraph(show_x=True, show_y=True, show_x_grid=True, autosize=True).handle_subject(
        go.Figure(go.Histogram(x=row_3[0])))

    seasons, this_year = (json.loads(_) for _ in row_3[2])
    airing = json.loads(row_3[1])

    handler_for_pies = BeautifyMyGraph(mt=30, mb=30, ml=30, mr=30, pad=100)

    yield False if not seasons["data"] else handler_for_pies.handle_subject(go.Figure(
        go.Pie(
            labels=[_.capitalize() for _ in seasons["index"]], values=seasons["data"],
            title=dict(text="Animes watched per Seasons")
        )
    )), False if not this_year["data"] else handler_for_pies.handle_subject(go.Figure(
        go.Pie(
            labels=[_.capitalize() for _ in this_year["index"]], values=this_year["data"],
            title=dict(text="This year watched")
        )
    ))

    yield False if not airing["data"] else handler_for_pies.handle_subject(
        go.Figure(
            go.Pie(
                labels=airing["index"], values=airing["data"],
                title=dict(text="Currently Airing"),
            ),
        )
    )
