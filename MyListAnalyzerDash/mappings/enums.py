from collections import namedtuple

main_app = namedtuple("MainApplication", [
    "loadApp", "loadingProps", "about", "repo", "body", "me"
])(
    "__app_load", {"variant": "bars", "color": "orange", "size": "xl"},
    "_about_mal-r", "https://github.com/RahulARanger/MyListAnalyzer", "dashboard-body", "logged-in-user"
)

home_page = namedtuple("HomePage", [
    "url", "name", "description", "github_logo", "greet", "apps", "home"
])(
    "/MLA/", "Home", "Home Page of the MyListAnalyzer, please check the Test Cases tab",
    "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", "Allow MyListAnalyzer to access your,",
    [
        ["View Dashboard", "/MLA/view/", "Dashboard for MyAnimeList Users"],
        ["View - Recently Dashboard", "/MLA/view-recently/", "Dashboard for the Recent Added Animes for Users"]
    ], "mal-home"
)

view_header = namedtuple(
    "ViewHeader",
    [
        "settings", "askName", "getName", "requestDetails",
        "re_fetch", "genresCount", "studiosCount", "addUser", "giveName", "appName", "short_name",
        "home", "show_name", "resultForSearch", "validateNote", "settingsTabs", "addImage",
        "searchAlert", "ask_again_image", "last_updated", "menu", "downloading", "timeStamp",
        "is_it_u", "stampsModal", "ask_for_nsfw"
    ]
)(
    "view-settings", "ask-user-name", "get-user-name", "request-details",
    "data-descriptive-fetch", "genres-count", "studios-count",
    'https://api.iconify.design/ant-design/user-add-outlined.svg?color=darkorange', "give-name", "MyListAnalyzer",
    "MLA",
    "/MLA", "mla-view-show-name", "validate-mal-user-result", "user-validate-check", "view-settings-tabs",
    "https://api.iconify.design/line-md/plus.svg?color=darkorange",
    "We can only search for the public users and If you are logged in then you can directly search for yourself.",
    "https://api.iconify.design/line-md/rotate-270.svg?color=green",
    "last-asked-user-details-job-mla",
    "https://api.iconify.design/line-md/close-to-menu-transition.svg?color=darkorange",
    "'https://api.iconify.design/line-md/downloading-loop.svg?color=darkorange",
    "https://api.iconify.design/mdi/recent.svg?color=gold",
    "view-user-for-you", "view-store-stamps-last-updated-mla", "ask_that_one_too"
)

view_dashboard = namedtuple(
    "viewDashBoard",
    [
        "locationChange", "intervalAsk",
        "startDetails", "tabs", "page_settings",
        "userJobDetailsNote",
        "row_1_colors", "tab_names",
        "no_data", "loadingNote", "time_spent_color", "process_again",
        "currently_airing", "clickToGoCards",
        "rating_dist", "ep_dist"
    ]
)(
    "user-view-location", "user-view-ask",
    "start-details-fetch-view", "view-dashboard-tabs", "mla-page_settings",
    "note-user-job-details",
    ["teal", "blue", "pink"], ["Overview", "Recently"],
    "https://api.iconify.design/line-md/cloud-off-outline-loop.svg?color=gray",
    "loading-user-details-view",
    "indigo", "run-process-job-again-view-mla",
    "currently_airing_cards", "currently-airing-cards-swiped-to",
    "rating_dist_overview_mla", "ep_dist_overview_mla"
)

creds_modal = namedtuple(
    "CredsModal", [
        "notify", "client_name", "login", "pfp", "link_text", "logout",
        "location", "title", "description", "access", "loggedIn", "triggerId", "loadingNote", "last_prefix",
        "last_prefix_id", "logo"
    ]
)

mal_creds_modal = creds_modal(
    **{
        "notify": "allowNotificationManager-1",
        "client_name": "u_in_mal",
        "login": "ur-mal-login",
        "pfp": "ur-mal-pfp",
        "link_text": "MAL",
        "logout": "ur-mal-logout",
        "location": "ur-mal-location",
        "title": "MyAnimeList Login",
        "description": "By Logging in with MAL, you agree with certain things,",
        "access": "Note: No Data will be stored on server side. So you can login without worrying about it.",
        "loggedIn": "Logged in MyAnimeList Successfully",
        "triggerId": "trigger_modal_for_mal",
        "loadingNote": "loading-process-mal",
        "last_prefix": "Last Logged In: ",
        "last_prefix_id": "mal_last_logged_in",
        "logo": "https://image.myanimelist.net/ui/OK6W_koKDTOqqqLDbIoPAiC8a86sHufn_jOI-JGtoCQ"
    })

css_classes = namedtuple(
    "CSSClasses",
    [
        "jump", "customButton", "home_card", "request_details", "number_counter", "as_percent",
        "time_format", "rank_index_format"
    ])(
    "do-jump", "custom-butt", "home_card", "request-details", "count-number", "percent-number",
    "need_to_time_format", "format_rank_index"
)

_status_map = namedtuple(
    "Status", [
        "watching", "plan_to_watch", "completed", "on_hold", "dropped"
    ]
)

status_colors = _status_map("blue", "indigo", "green", "yellow", "red")
status_light_colors = _status_map("#2B4F60", "#FF8243", "#FFCB42", "#FFE300", "#E64848")
status_labels = _status_map("Watching", "Planned to Watch", "Watched", "Paused", "Stopped")
recent_status = namedtuple(
    "Status", [
        "Watching", "Completed", "Hold", "Dropped"
    ])

recent_status_color = recent_status("blue", "green", "yellow", "red")

header_menu_item = namedtuple("MenuItem", [
    "id", "title", "image_src", "desc"
])

header_menu_id = "search_user_name_view"

header_menu_items = [
    header_menu_item(
        header_menu_id, "Search User",
        "https://api.iconify.design/line-md/search-twotone.svg?color=lightblue",
        "Want to change the user ?, you can search here"
    ),
    header_menu_item(
        "filter-user-view-anime-list", "Filters",
        "https://api.iconify.design/line-md/coffee-twotone-loop.svg?color=darkorange"
        "&flip=vertical", "You can apply filters on various things before fetching"),
    header_menu_item(
        view_dashboard.process_again, "Fetch Again",
        "https://api.iconify.design/line-md/download-loop.svg?color=lightgreen",
        "For re-calculating things in the current active tab")
]

mla_stores = namedtuple(
    "Store", [
        "anime_list", "recent_anime_list", "tempDataStore"
    ]
)("user-anime-list-mla-view", "user-recent-anime-list-mla-view", "temp-user-anime-list")


recent_anime_list = header_menu_item(
    "_", "Recent Anime List",
    header_menu_items[2].image_src,
    "User's list of Animes that were updated recently"
)


helper = namedtuple(
    "HelperIcon", [
        "open",
        "info"
    ]
)(
    "https://api.iconify.design/material-symbols/open-in-new-sharp.svg?color=gray",
    "https://api.iconify.design/ic/round-info.svg?color=lightblue"
)


special_card_for_anime = namedtuple(
    "SpecialAnimeCard",
    [
        "key", "label", "color"
    ], defaults=dict(color="yellow")
)

overview_cards = [
    special_card_for_anime("pop", "Popular Anime", "yellow"),
    special_card_for_anime("recent", "Most Recently Updated", "orange"),
    special_card_for_anime("top", "Top Scoring Anime", "gray"),
    special_card_for_anime("oldest", "Oldest Anime", "grape"),
    special_card_for_anime("recently_completed_movie", "Recent Movie Completed", "indigo"),
    special_card_for_anime("longest_spent", "Longest Time Spent", "blue")
]
