import json
import typing
from datetime import datetime
import dash_mantine_components as dmc
import plotly.colors as colors
import plotly.graph_objects as go
from dash import dcc, callback, Output, State, Input, MATCH, clientside_callback, ClientsideFunction, ALL, \
    html, no_update
from MyListAnalyzerDash.Components.cards import number_card_format_1, no_data, error_card, splide_container, \
    SplideOptions, number_card_format_3, card_format_4, relative_color, special_anime_card
from MyListAnalyzerDash.Components.graph_utils import BeautifyMyGraph, Config, core_graph
from MyListAnalyzerDash.Components.layout import expanding_row, expanding_layout
from MyListAnalyzerDash.mappings.enums import view_dashboard, status_colors, status_labels, status_light_colors, \
    mla_stores, helper, overview_cards
from MyListAnalyzerDash.utils import genre_link, studio_link, basic_swiper_structure
from MyListAnalyzerDash.Components.buttons import icon_butt_img
from MyListAnalyzerDash.Components.ModalManager import make_modal_alive, get_modal, get_modal_id
from MyListAnalyzerDash.Components.table import MakeTable


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
            [
                Output(dict(type=postfix_tab, index=view_dashboard.tab_names[0]), "children"),
                Output(get_modal_id(view_dashboard.showMoreAbtSpecial), "children")
            ],
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

        make_modal_alive(view_dashboard.showMoreAbtSpecial, ask_first=False)

    @property
    def modals(self):
        yield get_modal(
            view_dashboard.showMoreAbtSpecial,
            "Know more"
        )

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
            ), no_update

        tab_index = 0
        page, graph_class = self.tab_details(tab_index)
        user_name = page_settings.get("user_name")

        try:
            cards = general_info(data, page)
            belt, table = self.special_anime_belt_in_overview(data, tab_index)
            time_spent = data.get("time_spent", "Not Known")
            second_row = status_dist(data, page)
            status_for_airing_ones_in_list = self.currently_airing_details(data, user_name, tab_index)
            ep_range = self.episode_range(data, tab_index)
            rating_dist = self.rating_dist(data, tab_index)

        except Exception as error:
            return error_card("Failed to plot results: %s, Might be server returned invalid results" % (repr(error),))

        spent_container = basic_swiper_structure(
            "time_spent",
            *(number_card_format_1(
                number=spent[0], label=spent[1], color=view_dashboard.time_spent_color, class_name=page,
                main_class="swiper-slide", is_percent=False
            )
                for spent in time_spent)
        )

        cards.insert(1, spent_container)

        gap = "3px"

        first_row = expanding_row(
            *cards,
            style=dict(gap="6px")
        )

        third_row = expanding_row(
            number_card_format_1(
                number=data.get("eps_watched", 0), is_percent=False,
                label="# Eps. Watched", class_name=page,
                color="grape"
            ),
            number_card_format_1(
                number=data.get("avg_score", 0) if data.get("avg_score", 0) else "No scores given yet",
                is_percent=False,
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
            style=dict(gap=gap)
        )

        fourth_row = expanding_row(
            ep_range, rating_dist,
            style=dict(alignContent="center", alignItems="center", justifyContent="center", gap=gap)
        )

        rows = expanding_row(
            expanding_layout(
                first_row, second_row, third_row,
                position="flexStart", no_wrap=True
            ),
            status_for_airing_ones_in_list,
            style=dict(alignItems="center")
        )

        return [
            __ for _ in (belt, rows, fourth_row) for __ in
            [_, dmc.Space(h=3), dmc.Divider(color="dark", style={"opacity": 0.5}), dmc.Space(h=1)]
        ], table

    def process_recently_data(self, data, page_settings):
        if not data:
            return no_data(
                "Please wait until the data gets processed.", force=True
            )

        current_tab, graph_class = self.tab_details(1)

        user_name = page_settings.get("user_name", "")
        recently_updated_animes = json.loads(data.get("recently_updated_animes", "{}"))

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
            type="loop", width="", perPage=4, gap=".69rem", padding="6px", autoplay=True,
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

    def special_anime_belt_in_overview(self, data, index):
        class_name, _ = self.tab_details(index)
        specials = data.get("specials", {})

        cards = []
        raw = {}

        tabs = []
        tab_children = []
        first = None

        for card in overview_cards:
            if not specials.get(card.key, False):
                continue

            if not first:
                first = card.key

            value = json.loads(specials.get(card.key))
            raw[card.label] = value
            cards.append(
                special_anime_card(
                    value["node.title"],
                    "/", value["node.main_picture.large"],
                    card.label, card.color
                )
            )

            tabs.append(dmc.Tab(card.label, value=card.key))
            table = MakeTable()
            table.set_headers(("Key", "Value"))

            for key, value in value.items():
                table.add_cell(key)
                table.add_cell(value)
                table.make_row()

            tab_children.append(dmc.TabsPanel(table(), value=card.key))

        splide_options = SplideOptions(
            type="loop", width="", perPage=4, gap=".69rem", padding="6px", autoplay=True,
            **SplideOptions.with_breakpoints()
        )

        if first:
            table = dmc.Tabs([dmc.TabsList(tabs), *tab_children], value=first)
        else:
            table = "No Data Found"

        return html.Section([
            splide_container(
                *cards, splide_options=splide_options, class_name=f"belt {class_name}"
            ),
            html.Span(icon_butt_img(
                helper.open, view_dashboard.showMoreAbtSpecial
            ), style=dict(position="absolute", top="3px", right="10px")),
        ]), table

    def currently_airing_details(self, data, user_name, index):
        prefix, class_name = self.tab_details(index)

        airing = json.loads(data.get("status_for_currently_airing", "{}"))
        if not airing["data"]:
            return dmc.Alert(
                dmc.Text(f"{user_name} is not Watching any Animes which are currently airing"),
                color="dark", title="No Data",
                variant="filled", style=dict(maxWidth="300px"),
                icon=[dmc.Image(src=view_dashboard.no_data)])

        figure = go.Figure(
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

        return core_graph(
            BeautifyMyGraph(
                title="Currently Airing"
            ).handle_subject(figure), apply_shimmer=False, index=1,
            prefix=prefix, class_name=class_name, responsive=True)

    def episode_range(self, data, index):
        raw = json.loads(data.get("ep_range", "{}"))
        prefix, class_name = self.tab_details(index)

        fig = go.Figure()
        x = tuple(raw.get("key_0", {}).values())
        y = tuple(raw.get("ep_range", {}).values())
        _colors = [
            colors.qualitative.Dark2[1] if int(_color) else colors.qualitative.Set2[2] for _color in
            raw.get("color", {}).values()]

        bar_trace = go.Bar(
            x=x, y=y, text=y, textposition="auto",
            marker=dict(
                color=_colors,
                line=dict(width=2, color="#18191A")),
            hovertemplate="<b>[%{x}]</b>: %{y}<extra></extra>"
        )
        fig.add_trace(bar_trace)

        ep_range = Config()
        ep_range.scroll_zoom = False

        return core_graph(
            BeautifyMyGraph(
                title="Range of Anime Episodes", x_title="Episode Range", y_title="Anime Count",
                show_x=True, show_y=True, show_y_grid=True, autosize=True).handle_subject(fig),
            apply_shimmer=False, index=2, prefix=prefix, class_name=class_name,
            responsive=True, config=ep_range
        )

    def rating_dist(self, data, index):
        prefix, class_name = self.tab_details(index)

        rating_dist = json.loads(data.get("rating_dist", {}))
        ratings = tuple(rating_dist.keys())
        values = tuple(rating_dist.values())

        figure = go.Figure(
            go.Pie(
                labels=ratings, values=values,
                textinfo="label+percent",
                marker=dict(
                    colors=colors.sequential.Burg,
                    line=dict(width=.69, color=colors.sequential.Burg[-1])
                )
            ),
        )

        return core_graph(
            BeautifyMyGraph(
                title=f"Age Rating over the animes",
                mt=10
            ).handle_subject(figure), apply_shimmer=False, index=3,
            prefix=prefix, class_name=class_name, responsive=True)


def general_info(data, page):
    row_1 = data["row_1"]
    # SAMPLE: {'values': [111, 2, 8], 'keys': ['Total Animes', 'Watching', 'Not Yet Aired']}
    return [
        number_card_format_1(
            number=value, label=label,
            color=color, class_name=page, is_percent=False)
        for label, value, color in zip(row_1.get("keys", []), row_1.get("values", []), view_dashboard.row_1_colors)
    ]


def status_dist(data, page):
    row_2 = json.loads(data["row_2"])
    # SAMPLE: {
    # 'index': ['completed', 'plan_to_watch', 'on_hold', 'dropped'],
    # 'data': [[69, 62.1621621622], [37, 33.33333], [2, 1.8018], [1, 0.9009]]}

    return expanding_row(*(
        number_card_format_1(
            number=number, is_percent=True, label=getattr(status_labels, index).capitalize(),
            class_name=page, another=exact,
            color=getattr(status_colors, index)
        ) for index, (exact, number) in zip(row_2.get("index", []), row_2.get("data"))
    ), style=dict(gap="4px"))


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

