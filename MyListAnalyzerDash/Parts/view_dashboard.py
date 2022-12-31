import json
import typing
from datetime import datetime

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, callback, Output, State, Input, MATCH, clientside_callback, ClientsideFunction, ALL, \
    html
from dash.dash_table import DataTable

from MyListAnalyzerDash.Components.cards import number_card_format_1, no_data, error_card, splide_container, \
    SplideOptions, number_card_format_3, card_format_4, relative_color
from MyListAnalyzerDash.Components.collection import fixed_menu
from MyListAnalyzerDash.Components.graph_utils import BeautifyMyGraph, Config, core_graph, style_dash_table
from MyListAnalyzerDash.Components.layout import expanding_row, expanding_layout
from MyListAnalyzerDash.mappings.enums import view_dashboard, status_colors, status_labels, status_light_colors, mla_stores
from MyListAnalyzerDash.utils import genre_link, studio_link


class ViewDashboard:
    def __init__(self):
        self.postfix_tab = "-tab"
        self.tab_butt = "-button"
        self.graph_prefix = "-graphs"

    def connect_callbacks(self):
        postfix_tab = view_dashboard.tabs + self.postfix_tab

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
                Output(mla_stores.anime_list, "data"),
                Output(mla_stores.recent_anime_list, "data"),
                Output(view_dashboard.process_again, "id")
            ],
            [
                Input(view_dashboard.intervalAsk, "disabled"),
                Input(view_dashboard.tabs, "value"),
                Input(view_dashboard.process_again, "n_clicks")
            ],
            [
                # Timer Status
                State(view_dashboard.startButtTrigger, "color"),
                # BackEnd URL
                State("pipe", "data"),
                # tab_labels
                State(dict(type=postfix_tab, index=ALL), "id"),
                # Data Sources
                State(view_dashboard.page_settings, "data"),
                State(dict(type=view_dashboard.tempDataStore, index=ALL), "data"),
                State(mla_stores.anime_list, "data"),
                State(mla_stores.recent_anime_list, "data"),
                State(dict(type=view_dashboard.tabs, index=ALL), "data")
            ]
        )

        callback(
            Output(dict(type=postfix_tab, index=view_dashboard.tab_names[0]), "children"),
            [
                Input(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[0]), "data"),
                Input(view_dashboard.page_settings, "data")
            ]
        )(self.process_for_overview)

        callback(
            Output(dict(type=postfix_tab, index=view_dashboard.tab_names[1]), "children"),
            [
                Input(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[1]), "data"),
                Input(view_dashboard.page_settings, "data")
            ]
        )(self.process_recently_data)

    def layout(self, page_settings):
        postfix_tab = view_dashboard.tabs + self.postfix_tab
        tab_butt = view_dashboard.tabs + self.tab_butt

        tabs = []
        store = []
        tab_panels = []

        for index, page in enumerate(view_dashboard.tab_names):
            if index != 1 and page_settings.get("disable_user_job", False):
                continue

            tabs.append(dmc.Tab(page, value=page))

            tab_panels.append(dmc.TabsPanel(
                children=dmc.Skeleton(dmc.Paper(
                    no_data("Please wait until results are fetched", force=True),
                    pr=15, pb=5, mb=10,
                    id=dict(type=postfix_tab, index=page), style={"backgroundColor": "transparent"}),
                    visible=False, animate=True), value=page, id=dict(type=tab_butt, index=page)))
            store.append(
                dcc.Store(storage_type="memory", id=dict(type=view_dashboard.tabs, index=page), data="")
            )

        return html.Section([
            dmc.Tabs(
                children=[
                    dmc.TabsList(tabs), dmc.Space(h=6), *tab_panels, dmc.Space(h=3)
                ], color="orange",
                style={"fontSize": "0.5rem"}, id=view_dashboard.tabs, persistence="true",
                persistence_type="memory", value=view_dashboard.tab_names[0]),
            *store
        ])

    def tab_details(self, index=0):
        current_tab = view_dashboard.tab_names[index]
        graph_class = current_tab + self.graph_prefix
        return current_tab, graph_class

    def process_for_overview(self, data, page_settings):
        if not data:
            return no_data(
                "Please wait until the data gets processed.", force=True
            )

        page, graph_class = self.tab_details(0)
        user_name = page_settings.get("user_name")

        try:
            time_spent, row_1, row_2, rating_over_years, ep_range, wht_the_dog_dng, wht_the_dog_dng_know_more = process_for_overview(
                data, page, graph_class, user_name)
        except Exception as error:
            return error_card("Failed to plot results: %s, Might be server returned invalid results" % (repr(error),))

        cards = [
            number_card_format_1(
                number=value, label=label,
                color=color, class_name=page, is_percent=False)
            for value, label, color in row_1
        ]

        spent_container = splide_container(*(
            number_card_format_1(
                number=spent[0], label=spent[1], color=view_dashboard.time_spent_color, class_name=page,
                is_percent=False
            )
            for spent in time_spent
        ), splide_options=SplideOptions(autoplay=True, type="loop", width="210px"))

        cards.insert(1, spent_container)

        first_row = expanding_row(*cards, style=dict(justifyContent="center"))

        second_row = expanding_row(*(
            number_card_format_1(
                number=value, is_percent=True, label=label.capitalize(),
                class_name=page, another=exact,
                color=color
            ) for label, (exact, value), color in row_2
        ))

        third_row = expanding_row(
            number_card_format_1(
                number=data.get("eps_watched", 0), is_percent=False,
                label="# Eps. Watched", class_name=page,
                color="grape"
            ),
            number_card_format_1(
                number=data.get("avg_score", 0), is_percent=False,
                label="Mean Score", class_name=page,
                color=relative_color(data.get("avg_score", 0), 10)
            ),
            card_format_4(
                data.get("mostly_seen_genre", ""),
                "Mostly seen Genre",
                "orange", page, url=genre_link(data.get("genre_link"))
            ),
            card_format_4(
                data.get("mostly_seen_studio", ""),
                "Mostly seen Studio",
                "cyan", page, url=studio_link(data.get("studio_link"))
            ),
            style=dict(gap="1rem", alignContent="center", alignItems="center", justifyContent="center")
        )

        fourth_row = expanding_row(
            wht_the_dog_dng, ep_range,
            style=dict(gap="1rem", alignContent="center", alignItems="center", justifyContent="center")
        )

        fifth_row = rating_over_years

        return [
            __ for _ in (first_row, second_row, third_row, fourth_row, fifth_row) for __ in
            [_, dmc.Space(h=3), dmc.Divider(color="dark", style={"opacity": 0.5}), dmc.Space(h=3)]
        ]

    def process_recently_data(self, data, page_settings):
        if not data:
            return no_data(
                "Please wait until the data gets processed.", force=True
            )

        current_tab, graph_class = self.tab_details(1)

        user_name = page_settings.get("user_name", "")
        recently_updated_animes = json.loads(data.get("recently_updated_animes", "{}"))

        # menu = fixed_menu(
        #     side_ways=[
        #         dmc.Text(expanding_layout(
        #             dmc.Text(user_name, color="orange", size="sm"), f"last Updated:",
        #             relative_time_stamp_but_calc_in_good_way(
        #                 False, class_name=css_classes.time_format, default=data["recently_updated_at"]
        #             ), direction="row"
        #         ), size="sm")
        #     ]
        # )

        recently_updated_plots = recently_updated_trend_comp(
            json.loads(data.get("recently_updated_day_wise", "{}")),
            data.get("recently_updated_cum_sum", []),
            current_tab, graph_class, user_name
        )

        cards = [
            number_card_format_3(
                current_tab, index, *_
            ) for index, _ in enumerate(recently_updated_animes)
        ]

        splide_options = SplideOptions(
            type="loop", width="", perPage=4, gap=".69rem", padding="6px", autoScroll=dict(speed=1),
            mediaQuery="max",
            breakpoints={
                "1120": dict(perPage=3.5),
                "980": dict(perPage=3),
                "860": dict(perPage=2.5),
                "740": dict(perPage=2),
                "620": dict(perPage=1.5),
                "420": dict(perPage=1.25),
                "300": dict(perPage=1)
            }
        )

        belt = splide_container(*cards, splide_options=splide_options, class_name=current_tab)

        return expanding_layout(
            dmc.Space(h=3), belt, dmc.Space(h=2), recently_updated_plots
        )


def process_for_overview(data, current_tab, graph_class, user_name):
    row_1 = data["row_1"]
    time_spent = data["time_spent"]
    row_2 = json.loads(data["row_2"])
    ep_range_raw, airing_dist, airing_detail = data["row_3"]

    rating_over_years = data["rating_over_years"]

    yield time_spent
    yield zip(row_1["values"], row_1["keys"], view_dashboard.row_1_colors)

    yield zip(
        map(lambda x: getattr(status_labels, x), row_2["index"]),
        row_2["data"], map(lambda x: getattr(status_colors, x), row_2["index"])
    )
    # above is for the cards

    ep_range = Config()
    ep_range.scroll_zoom = False

    ratings = rating_over_years["ratings"]

    fig = go.Figure(
        data=[go.Bar(x=ratings, y=rating_over_years["frames"][0])],
        layout=go.Layout(
            yaxis=dict(range=[0, rating_over_years["max_y_range"]], autorange=False),
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None])])]
        ),
        frames=[go.Frame(data=[go.Bar(x=ratings, y=value)]) for value in rating_over_years["frames"][1:]]
    )

    yield core_graph(
        BeautifyMyGraph(
            title="Seasons over years", x_title="years", y_title="Seasons",
            show_x=True, show_y=True
        ).handle_subject(fig),
        apply_shimmer=False, index=3, prefix=current_tab, class_name=graph_class,
        responsive=True
    )

    yield core_graph(
        BeautifyMyGraph(
            title="Range of Anime Episodes", x_title="Episode Range", y_title="Number of Shows",
            show_x=True, show_y=True, show_y_grid=True, autosize=True).handle_subject(
            ep_bins_plot(json.loads(ep_range_raw))),
        apply_shimmer=False, index=1, prefix=current_tab, class_name=graph_class,
        responsive=True, config=ep_range
    )

    airing = json.loads(airing_dist)

    if not airing["data"]:
        yield dmc.Alert(
            dmc.Text(f"{user_name} is not Watching any Animes which are currently airing"),
            color="orange", title="No Data", withCloseButton=True,
            icon=[dmc.Image(src=view_dashboard.no_data)])
    else:
        yield core_graph(
            BeautifyMyGraph(
                title="Currently Airing"
            ).handle_subject(currently_airing_pie(airing)), apply_shimmer=False, index=2,
            prefix=current_tab, class_name=graph_class, responsive=True)

    yield airing_detail


def ep_bins_plot(series):
    fig = go.Figure()

    series["index"].pop()
    colors = series["data"].pop()

    bar_trace = go.Bar(
        x=series["index"], y=series["data"], text=series["data"], textposition="auto",
        marker=dict(color=colors, line=dict(width=2, color="#18191A")),
        hovertemplate="<b>[%{x}]</b>: %{y}<extra></extra>"
    )
    fig.add_trace(bar_trace)

    return fig


def currently_airing_pie(airing):
    return go.Figure(
        go.Pie(
            hovertemplate="<b>%{label}</b>: %{value} || %{percent}<extra></extra>",
            labels=tuple(map(lambda x: getattr(status_labels, x), airing["index"])), values=airing["data"],
            marker=dict(
                colors=tuple(map(lambda x: getattr(status_light_colors, x), airing["index"])),
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


def over_view_s_over_view(raw):
    table = dmc.MenuItem("Currently Airing - Table", color="orange")
    return fixed_menu(table)


def timely_updated_at(time_stamps: typing.Sequence[int], graph_class: str, tab_name: str):
    date_times = [
        datetime.fromtimestamp(time_stamp) for time_stamp in time_stamps
    ]

    violin_plot = go.Figure()
    violin_plot.add_trace(
        go.Violin(
            x=date_times
        )
    )

    return core_graph(
        BeautifyMyGraph(
            title="When did the User Update",
            show_x=True, show_y=True, show_x_grid=True, show_y_grid=True
        ).handle_subject(violin_plot), apply_shimmer=False, index=2,
        prefix=tab_name, class_name=graph_class, responsive=True)


def recently_updated_trend_comp(recently_updated_data, cum_sum, tab_name, graph_class, user_name):
    to_dates = [
        datetime(*_)
        for _ in recently_updated_data.get("columns", [])
    ]

    up_until, total, diff, not_comp, re_watched = recently_updated_data.get("data", [tuple() for _ in range(5)])

    plot_with_actual_data = go.Figure()
    plot_with_cum_sum = go.Figure()

    marker = dict(color="darkorange")
    line = dict(shape="spline")
    mode = "markers+lines"

    trace = go.Scatter(
        x=to_dates, y=diff, mode=mode, marker=marker, line=line
    )

    plot_with_actual_data.add_trace(trace)

    trace = go.Scatter(
        x=to_dates, y=cum_sum, mode=mode, marker=marker, line=line)

    plot_with_cum_sum.add_trace(trace)

    plot_1 = core_graph(
        BeautifyMyGraph(
            title=f"Recently updated animes by days",
            show_x=True, show_y=True, show_x_grid=True, show_y_grid=True, hover_mode="x unified"
        ).handle_subject(plot_with_actual_data), apply_shimmer=False, index=1,
        prefix=tab_name, class_name=graph_class, responsive=True)

    plot_2 = core_graph(
        BeautifyMyGraph(
            title=f"{user_name}'s recent progressive updates",
            show_x=True, show_y=True, show_x_grid=True, show_y_grid=True, hover_mode="x unified"
        ).handle_subject(plot_with_cum_sum), apply_shimmer=False, index=2,
        prefix=tab_name, class_name=graph_class, responsive=True)

    _weeks = [
        _.strftime("%A") for _ in to_dates
    ]

    fig = go.Figure()
    trace = go.Violin(
        x=_weeks, y=diff
    )

    fig.add_trace(trace)

    weekly_fat = core_graph(
        BeautifyMyGraph(
            title=f"{user_name}'s weekly updates", show_x=True, show_x_grid=True, show_y=True
        ).handle_subject(fig),
        apply_shimmer=False, index=3, prefix=tab_name, class_name=graph_class, responsive=True
    )

    labels = ["Actual", "Cumulative", "Weekly"]

    tabs = [dmc.TabsPanel(children=plot_1, value=labels[0]),
            dmc.TabsPanel(children=plot_2, value=labels[1]),
            dmc.TabsPanel(
                value=labels[2],
                children=weekly_fat
            )]

    return dmc.Tabs(
        [
            *tabs, dmc.TabsList([dmc.Tab(_, value=_) for _ in labels])
        ], color="orange", variant="pills", value="Actual", persistence=True, persistence_type="session"
    )
