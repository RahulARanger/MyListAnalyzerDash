import json
import dash_mantine_components as dmc
from dash import dcc, callback, Output, State, Input, MATCH, clientside_callback, ClientsideFunction, ALL, \
    html
from MyListAnalyzerDash.Components.cards import number_card_format_1, no_data, error_card, card_format_4, \
    relative_color, special_anime_card, number_comp, currently_airing_card, number_card_format_3
from MyListAnalyzerDash.Components.layout import expanding_row, expanding_layout
from MyListAnalyzerDash.Components.tooltip import set_tooltip
from MyListAnalyzerDash.mappings.enums import view_dashboard, status_colors, status_labels, mla_stores, overview_cards
from MyListAnalyzerDash.utils import genre_link, studio_link, basic_swiper_structure, anime_link


class ViewDashboard:
    def __init__(self):
        self.postfix_tab = "-tab"
        self.tab_butt = "-button"
        self.graph_prefix = "-graphs"

    def connect_callbacks(self):
        prefix = view_dashboard.tabs + self.postfix_tab

        clientside_callback(
            ClientsideFunction(
                namespace="MLA",
                function_name="refreshTab"
            ),
            Output(dict(type=prefix, index=MATCH), "id"),
            Input(dict(type=prefix, index=MATCH), "children"),
            State(dict(type=prefix, index=MATCH), "id")
        )  # this happens when data is changed

        clientside_callback(
            ClientsideFunction(
                namespace="MLA",
                function_name="processUserDetailsWhenNeeded"
            ),
            [
                Output(dict(type=view_dashboard.tabs, index=ALL), "data"),
                Output(view_dashboard.userJobDetailsNote, "children"),  # notification
                Output(mla_stores.anime_list, "data"),
                Output(mla_stores.recent_anime_list, "data"),
                Output(view_dashboard.process_again, "id")
            ],
            [
                Input(mla_stores.tempDataStore, "data"),
                Input(view_dashboard.tabs, "value"),
                Input(view_dashboard.process_again, "n_clicks")
            ],
            [
                # Timer Status
                # BackEnd URL
                State("pipe", "data"),
                # tab_labels
                State(dict(type=prefix, index=ALL), "id"),
                # Data Sources
                State(view_dashboard.page_settings, "data"),
                State(mla_stores.anime_list, "data"),
                State(mla_stores.recent_anime_list, "data"),
                State(dict(type=view_dashboard.tabs, index=ALL), "data")
            ]
        )

        callback(
            Output(dict(type=prefix, index=view_dashboard.tab_names[0]), "children"),
            [
                Input(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[0]), "data"),
                Input(view_dashboard.page_settings, "data")
            ]
        )(self.process_for_overview)

        callback(
            Output(dict(type=prefix, index=view_dashboard.tab_names[1]), "children"),
            [
                Input(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[1]), "data"),
                Input(view_dashboard.page_settings, "data")
            ]
        )(self.process_recently_data)

        clientside_callback(
            ClientsideFunction(
                function_name="plotForOverviewTab",
                namespace="MLAPlots"
            ),
            Output(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[0]), "id"),
            Input(dict(type=prefix, index=view_dashboard.tab_names[0]), "children"),
            State(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[0]), "data")
        )

        clientside_callback(
            ClientsideFunction(
                function_name="plotForRecentlyTab",
                namespace="MLAPlots"
            ),
            Output(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[1]), "id"),
            Input(dict(type=prefix, index=view_dashboard.tab_names[1]), "children"),
            [
                State(dict(type=view_dashboard.tabs, index=view_dashboard.tab_names[1]), "data"),
                State(view_dashboard.page_settings, "data"),
                State(mla_stores.recent_anime_list, "data")
            ]
        )

        clientside_callback(
            ClientsideFunction(
                function_name="clickToGoCardIndex",
                namespace="MLA"
            ),
            Output(dict(index=MATCH, section=view_dashboard.clickToGoCards), "id"),
            Input(dict(index=MATCH, section=view_dashboard.clickToGoCards), "n_clicks"),
            [
                State(dict(index=MATCH, section=view_dashboard.clickToGoCards), "id"),
                State(view_dashboard.currently_airing, "id")
            ]
        )

    def layout(self, page_settings):
        postfix_tab = view_dashboard.tabs + self.postfix_tab
        tab_butt = view_dashboard.tabs + self.tab_butt

        tabs = []
        store = []
        tab_panels = []

        user_job_disabled = page_settings.get("disable_user_job", False)

        for index, page in enumerate(view_dashboard.tab_names):
            if index != 1 and user_job_disabled:
                continue

            tabs.append(dmc.Tab(page, value=page))

            tab_panels.append(dmc.TabsPanel(
                children=dmc.Skeleton(dmc.Paper(
                    no_data("Please wait until results are fetched", force=True),
                    pr=15, pb=5, mb=10,
                    id=dict(type=postfix_tab, index=page), style={"backgroundColor": "transparent"}),
                    visible=False, animate=True), value=page, id=dict(type=tab_butt, index=page), p=6))
            store.append(
                dcc.Store(storage_type="memory", id=dict(type=view_dashboard.tabs, index=page), data="")
            )

        return html.Section([
            dmc.Tabs(
                children=[
                    dmc.TabsList(tabs), dmc.Space(h=6), *tab_panels, dmc.Space(h=3)
                ], color="orange",
                style={"fontSize": "0.5rem"}, id=view_dashboard.tabs, persistence="true",
                persistence_type="memory", value=view_dashboard.tab_names[int(user_job_disabled)]),
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

        tab_index = 0
        page, graph_class = self.tab_details(tab_index)
        user_name = page_settings.get("user_name")

        try:
            cards = general_info(data, page)
            belt = self.special_anime_belt_in_overview(data, tab_index, user_name)
            time_spent = data.get("time_spent", "Not Known")
            second_row = status_dist(data, page)
            status_for_airing_ones_in_list = self.currently_airing_details(data, user_name, tab_index)

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
            *cards, style=dict(gap=gap, justifyContent="center")
        )

        third_row = expanding_row(
            number_card_format_1(
                number=data.get("eps_watched", 0), is_percent=False,
                label="# Eps. Watched", class_name=page,
                color="grape.6"
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
                "orange.5", page, url=genre_link(data.get("genre_link"))
            ),
            card_format_4(
                data.get("mostly_seen_studio", ""),
                "Mostly seen Studio",
                "cyan", page, url=studio_link(data.get("studio_link"))
            ),
            style=dict(gap=gap, justifyContent="center")
        )

        fourth_row = expanding_row(
            html.Article(id=view_dashboard.ep_dist, className=graph_class),
            html.Article(id="nsfw", className=graph_class),
            html.Article(id=view_dashboard.rating_dist, className=graph_class),
            style=dict(alignContent="center", alignItems="center", justifyContent="center", gap=gap)
        )

        rows = expanding_row(
            expanding_layout(
                first_row, second_row, third_row,
                position="flexStart", no_wrap=True
            ),
            status_for_airing_ones_in_list,
            style=dict(alignItems="center", gap=gap, justifyContent="center")
        )

        return [
            __ for _ in (belt, rows, fourth_row) for __ in
            [_, dmc.Space(h=2.5), dmc.Divider(color="gray.8"), dmc.Space(h=2.5)]
        ]

    def process_recently_data(self, data, page_settings):
        if not data:
            return no_data(
                "Please wait until the data gets processed.", force=True
            )

        tab_index = 1
        current_tab, graph_class = self.tab_details(tab_index)

        user_name = page_settings.get("user_name", "")

        charts = [
            "daily-weightage",
            "quick-update-history",
            "weekly-progress-recently-view",
        ]

        row_1 = expanding_row(
            html.Div(id=charts[0], className=graph_class),
            html.Div(id=charts[1], className=graph_class),
            style=dict(gap="3px")
        )

        race = html.Div(id=charts[2], className=graph_class)

        return expanding_layout(
            row_1,
            expanding_row(
                race, special_results_for_recent_animes(data.get("special_results"), user_name),
                style=dict(alignItems="center")
            ),
            spacing="sm"
        )

    def special_anime_belt_in_overview(self, data, index, user_name):
        class_name, _ = self.tab_details(index)
        specials = data.get("specials", {})

        cards = []
        raw = {}

        for card in overview_cards:
            if not specials.get(card.key, False):
                continue

            value = specials.get(card.key)
            raw[card.label] = value

            name, _id, pic = value["general"]
            total, watched, spent, status = value["progress"]
            fav, start_date, end_date = value["required_parameters"]
            special_value, about = value["special"]
            _info = value["info"]
            info = [
                dmc.Text(f"{user_name}'s Status", color="orange", italic=True),
                dmc.Text(f"Started at: {_info[0]}"),
                dmc.Text(f"Finished at: {_info[1]}"),
                dmc.Text(f"Last Updated at: {_info[-1]}")
            ]

            fav = number_comp(fav, False, "light", class_name, size="xs")

            progress = dmc.Progress(
                animate=status == "watching",
                striped=True,
                sections=[
                    dict(
                        value=100 if not total else ((watched / total) * 100),
                        color=getattr(status_colors, status),
                        tooltip=expanding_layout(
                            dmc.Text(f"Time Spent: {spent} hr{'s' if int(spent) > 1 else ''}"),
                            dmc.Text(f"Status: {getattr(status_labels, status)}"),
                            dmc.Text(f"Progress: {watched} / {total if total else 'NA'}")
                        )
                    )
                ]
            )

            cards.append(
                special_anime_card(
                    name, anime_link(_id), pic,
                    card.label, card.color,
                    progress,
                    about, special_value,
                    info,
                    fav, start_date, end_date,
                    class_name="swiper-slide"
                )
            )

        return basic_swiper_structure(
            "special_belt", *cards
        )

    def currently_airing_details(self, data, user_name, index):
        prefix, class_name = self.tab_details(index)

        currently_airing = json.loads(data.get("currently_airing_animes", "{}"))

        if not currently_airing.get("data", ""):
            return dmc.Alert(
                dmc.Text(f"{user_name} is not Watching any Animes which are currently airing"),
                color="dark", title="No Data",
                variant="filled", style=dict(maxWidth="300px"),
                icon=[dmc.Image(src=view_dashboard.no_data)])

        status_map = dict()
        animes = zip(currently_airing.get("index", []), currently_airing.get("data", []))

        cards = []

        for index, (anime_id, raw) in enumerate(animes):
            card, status = currently_airing_card(anime_id, *raw)
            cards.append(card)
            status_map[status] = status_map.get(status, index)

        inside_hover = expanding_layout(
            dmc.Divider(color="orange", size="lg", label="Currently Airing Animes ~ Recent 10", labelPosition="center"),
            expanding_row(
                *(
                    set_tooltip(
                        dmc.Button(
                            "".join([__[0].upper() for __ in _.split("_")]), color=getattr(status_colors, _), size="xs",
                            compact=True, id=dict(
                                index=status_map[_], section=view_dashboard.clickToGoCards
                            )),
                        label=_
                    )
                    for _ in status_map
                )
            )
        )

        return dmc.HoverCard(
            [
                dmc.HoverCardTarget(basic_swiper_structure(
                    view_dashboard.currently_airing, *cards
                )),
                dmc.HoverCardDropdown(inside_hover)
            ], className="airing_cards"
        )


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
    ), style=dict(gap="3px", justifyContent="center"))


def special_results_for_recent_animes(raw, user_name):
    rows = [
        number_card_format_3(
            raw[key]["id"], *json.loads(raw[key]["anime"]),
            special_color=special_color, special_label=special_label, class_name="swiper-slide"
        )

        for [special_color, special_label], key in
        zip(
            (
                ("green", "Recently Completed Anime"),
                ("blue", "Currently Watching Anime"),
                ("yellow", "Recently Set on Hold"),
                ("red", "Recently Dropped Anime"),
            ),
            ("Completed", "Watching", "Hold", "Dropped")
        ) if key in raw
    ]

    longest = json.loads(raw["longest"]["anime"])
    diff = set_tooltip(
        dmc.Badge(f"Total: {longest[3]} Eps.", color="pink.4"),
        label=f"Total Number of Episodes for this show"
    )
    rows.append(
        number_card_format_3(
            raw["longest"]["id"], *longest, diff, status_badge=False,
            special_label="Longest Anime", special_color="indigo", class_name="swiper-slide"
        )
    )

    bulk_updated = json.loads(raw["most_updated"])
    diff = set_tooltip(
        dmc.Badge(f"{bulk_updated[6]} Eps were updated", color="yellow"),
        label=f"{user_name} has updated {bulk_updated[6]} Eps at once"
    )
    rows.append(
        number_card_format_3(
            *bulk_updated, diff, status_badge=False,
            special_label="Largest Bulk change", special_color="teal", class_name="swiper-slide"
        )
    )

    long_time = raw["long_time"]
    rows.append(
        number_card_format_3(
            long_time["id"], *json.loads(long_time["anime"]), dmc.Badge(long_time["time_took"], color="orange.9"),
            special_color="cyan.5", special_label="Took Long time to reach here", class_name="swiper-slide"
        )
    )

    records = raw["many_records"]
    badge = set_tooltip(
        dmc.Badge(f"Appeared: {records['mode']}", color="yellow.8", size="sm"),
        label=f"Number of Times, {user_name} has updated this anime")

    rows.append(
        number_card_format_3(
            records["id"], *json.loads(records["anime"]), badge, special_color="lime.5",
            special_label="Largest Number of updates", class_name="swiper-slide"
        )
    )

    large_change = raw["still"]
    large_changed_anime = json.loads(large_change["anime"])
    rows.append(
        number_card_format_3(
            large_change["id"], *large_changed_anime,
            set_tooltip(
                dmc.Badge(f"Still: {large_changed_anime[2] - large_changed_anime[3]} eps."),
                label="Number of Eps. left for the completion"
            ),
            special_color="pink", special_label="Still has long way to complete", class_name="swiper-slide"
        )
    )

    long_anime = raw["longest_title"]
    longest = json.loads(long_anime["anime"])
    rows.append(
        number_card_format_3(
            long_anime["id"], *longest, dmc.Badge(f"{len(longest[1])} words", color="teal.8", size="sm"),
            special_color="gray", special_label="Longest Title", class_name="swiper-slide"
        )
    )

    return basic_swiper_structure(
        "special_belt_for_recent_animes", *rows
    )
