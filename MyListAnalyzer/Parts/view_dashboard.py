from dash import dcc, callback, Output, State, Input, MATCH, no_update, clientside_callback, ClientsideFunction, ALL, \
    html
import dash_mantine_components as dmc
from MyListAnalyzer.mappings.enums import view_dashboard, status_colors, status_labels, seasons_maps
from MyListAnalyzer.Components.cards import number_card_format_1, no_data, error_card, embla_container, \
    number_card_format_2
from MyListAnalyzer.Components.layout import expanding_row, expanding_layout
from MyListAnalyzer.Components.graph_utils import BeautifyMyGraph, Config, core_graph, style_dash_table
import json
import plotly.graph_objects as go
from dash.dash_table import DataTable


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
                    visible=False, animate=True), label=label))
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
        if not data:
            return no_data("Collections -> user details")

        current_tab = view_dashboard.tab_names[0]
        graph_class = current_tab + "-graphs"

        try:
            row_1, row_2, ep_range, seasonal_info, wht_the_dog_dng = process_overview(
                data, current_tab, graph_class)
        except Exception as error:
            return error_card("Failed to plot results: %s, Might be server returned invalid results" % (repr(error),))

        first_row = expanding_row(*(
            number_card_format_1(
                number=value, label=label,
                color=color, class_name=current_tab, is_percent=False)
            for value, label, color in row_1
        ))

        second_row = expanding_row(*(
            number_card_format_1(
                number=value, is_percent=True, label=label.capitalize(),
                class_name=current_tab, another=exact,
                color=color
            ) for label, (exact, value), color in row_2
        ))

        third_row = expanding_row(
            ep_range, seasonal_info, wht_the_dog_dng, style=dict(gap="1rem")
        )

        return [
            __ for _ in (first_row, second_row, third_row) for __ in
            [_, dmc.Divider(color="dark", style={"opacity": 0.5, "marginBottom": "2px"})]
        ]


def process_overview(data, current_tab, graph_class):
    row_1 = data["row_1"]
    row_2 = json.loads(data["row_2"])
    ep_range_raw, seasons_raw, airing_dist, airing_detail, current_year = data["row_3"]

    yield zip(row_1["values"], row_1["keys"], view_dashboard.row_1_colors)
    yield zip(
        map(lambda x: getattr(status_labels, x), row_2["index"]),
        row_2["data"], map(lambda x: getattr(status_colors, x), row_2["index"])
    )
    # above is for the cards

    ep_range = Config()
    ep_range.scroll_zoom = False

    yield core_graph(
        BeautifyMyGraph(
            title="Range of Anime Episodes", x_title="Episodes", y_title="Count",
            show_x=True, show_y=True, show_y_grid=True, autosize=True).handle_subject(
            ep_bins_plot(json.loads(ep_range_raw))),
        apply_shimmer=False, index=1, prefix=current_tab, class_name=graph_class,
        responsive=True, config=ep_range
    )

    seasons = []
    # not using generator as it becomes hard to read
    for raw, title in zip(seasons_raw, ("Up Until,", f"{current_year},")):
        loaded = json.loads(raw)

        seasons.append(
            expanding_layout(dmc.Text(title, size="sm"), *(
                number_card_format_2(
                    season.capitalize(), seasons_maps[season][0],
                    value=value[0], percent_value=value[1] * 100, class_name=current_tab,
                    color=seasons_maps[season][1])

                for [season, value] in zip(loaded["index"], loaded["data"])
            )))

    yield embla_container(
        *seasons, class_name=graph_class, id_=dict(index=2, type=current_tab)
    )

    airing = json.loads(airing_dist)

    if not airing["data"]:
        yield dmc.Text("Empty")
    else:
        yield embla_container(
            core_graph(
                BeautifyMyGraph(
                    title="Currently Airing"
                ).handle_subject(currently_airing_pie(airing)), apply_shimmer=False, index=3,
                prefix=current_tab, class_name=graph_class, responsive=True),
            gen_table_for_airing_details(json.loads(airing_detail)),
            class_name=current_tab
        )


def ep_bins_plot(series):
    fig = go.Figure()

    series["index"].pop()
    colors = series["data"].pop()

    bar_trace = go.Bar(
        x=series["index"], y=series["data"], text=series["data"], textposition="auto",
        marker=dict(color=colors, line=dict(width=2, color="#18191A")),
        hovertemplate="<b>Range: %{x}</b> %{y}"
    )
    fig.add_trace(bar_trace)

    return fig


def currently_airing_pie(airing):
    return go.Figure(
        go.Pie(
            hovertemplate="<b>%{label}</b><extra>%{percent} || %{value}</extra>",
            labels=tuple(map(lambda x: getattr(status_labels, x), airing["index"])), values=airing["data"],
            marker=dict(
                colors=tuple(map(lambda x: getattr(status_colors, x), airing["index"])),
                line=dict(width=2, color="#18191A")),
            textinfo="label+percent", pull=[
                0.2 if status_labels.watching == getattr(status_labels, _) else 0 for _ in airing["index"]]
        ),
    )


def gen_table_for_airing_details(raw):
    filter_options = dict(case="insensitive")
    cols = (dict(name="Title", id="node.title", filter_options=filter_options),
            dict(name="Status", id="list_status.status", filter_options=filter_options))
    style_header, style_data, style_cell = style_dash_table()

    return DataTable(
        data=raw, columns=cols,
        style_header=style_header, style_data=style_data, style_table=dict(
            minWidth="calc(150px + 3vw)", maxHeight="calc(100vh - 43vh - 69px)", overflowX="auto", overflowY="auto"),
        style_cell=style_cell,
        filter_action="native",
        sort_action="native",
    )
