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
        ["View Dashboard", "/MLA/view/", "Dashboard for MyAnimeList Users"]
    ], "mal-home"
)

view_header = namedtuple(
    "ViewHeader",
    [
        "settings", "askName", "getName", "requestDetails",
        "re_fetch", "genresCount", "studiosCount", "addUser", "giveName", "appName", "short_name",
        "home", "show_name", "resultForSearch", "validateNote", "settingsTabs", "settingsImage", "addImage",
        "searchAlert", "ask_again_image", "last_updated"
    ]
)(
    "view-settings", "ask-user-name", "get-user-name", "request-details",
    "data-descriptive-fetch", "genres-count", "studios-count",
    'https://api.iconify.design/ant-design/user-add-outlined.svg?color=darkorange', "give-name", "MyListAnalyzer",
    "MLA",
    "/MLA", "mla-view-show-name", "validate-mal-user-result", "user-validate-check", "view-settings-tabs",
    "https://api.iconify.design/line-md/beer-alt-filled-loop.svg?color=darkorange",
    "https://api.iconify.design/line-md/plus.svg?color=darkorange",
    "We can only search for the public users. If any filters needed beforehand, Please apply them as provided in the "
    "filters tab",
    "https://api.iconify.design/line-md/rotate-270.svg?color=green",
    "last-asked-user-details-job-mla"
)

dashboard = namedtuple(
    "Dashboard", ["header", "board", "dcc_graph", "tabRefresh", "whenDidRefresh"]
)("header", "board", "core-graph-", "tab-refresh", "tab-refresh-when-view")

view_dashboard = namedtuple(
    "viewDashBoard",
    [
        "collectThings", "userDetailsJobResult", "locationChange", "intervalAsk",
        "startDetails", "tabs", "stop_note", "start_note", "page_settings", "startButt", "stopButt", "paging",
        "startButtTrigger", "stopButtTrigger", "fetchStatus", "tempDataStore", "userJobDetailsNote",
        "row_1_colors", "tab_names", "no_data", "loadingNote", "time_spent_color", "process_again",
        "recent_anime"
    ]
)(
    "view-collect", "view-user-job", "user-view-location", "user-view-ask",
    "start-details-fetch-view", "view-dashboard-tabs",
    "Please Note, When Stopped, we will be deleting everything that was collected before",
    "Starting Timer...", "mla-page_settings",
    "https://api.iconify.design/codicon/run-above.svg?color=green",
    "https://api.iconify.design/codicon/run-errors.svg?color=red",
    "view-results-next-page", "start-interval-view", "stop-interval-view", "job-view-status", "job-raw-store-view",
    "note-user-job-details",
    ["teal", "blue", "pink"], ["Overview", "Recently"],
    "https://api.iconify.design/line-md/cloud-off-outline-loop.svg?color=gray",
    "loading-user-details-view",
    "indigo", "run-process-job-again-view-mla",
    "view-dashboard-recent-anime-view"
)

creds_modal = namedtuple(
    "CredsModal", [
        "notify", "client_name", "login", "pfp", "link_text", "link_id", "logout",
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
        "link_id": "ur-mal-link-id",
        "logout": "ur-mal-logout",
        "location": "ur-mal-location",
        "title": "MyAnimeList Login",
        "description": "By Logging in with MAL, you agree with certain things,",
        "access": "Please login if and only if you are okay for this application to utilize your data",
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
        "Watching", "Completed", "Hold"
    ])

recent_status_color = recent_status("blue", "green", "yellow")

seasons_maps = {
    "winter": ["https://api.iconify.design/game-icons/cold-heart.svg?color=lightblue", "gray"],
    "spring": ["https://api.iconify.design/ph/tree-fill.svg?color=green", "green"],
    "fall": ["https://api.iconify.design/noto/fallen-leaf.svg", "orange"],
    "summer": ["https://api.iconify.design/line-md/sun-rising-filled-loop.svg?color=darkorange", "yellow"]
}
