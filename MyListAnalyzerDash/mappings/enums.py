from collections import namedtuple

main_app = namedtuple("MainApplication", [
    "loadApp", "loadingProps", "about", "repo", "body", "me", "collections"
])(
    "__app_load", {"variant": "bars", "color": "orange", "size": "xl"},
    "_about_mal-r", "https://github.com/RahulARanger/MyListAnalyzer", "dashboard-body", "logged-in-user",
    "user-collections-mla"
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

main_page_dashboard = namedtuple("MainPageDashBoard", [
    "tab", "tabIDs", "checks", "pages", "segment", "color_map", "intro_cards", "general_pies"
])(
    "tabs-for-main-page-dashboard", [
        "general",
        "recent",
        "overview"
    ], "dashboard-check", "paginate-graph", "graph-option-segment", {
        "completed": "green", "plan_to_watch": "yellow", "dropped": "red", "on_hold": "orange"
    }, [["teal", "indigo", "blue", "pink"], ["Total Animes", "Time Spent (hrs)", "Watching", "Not yet Aired"]],
    "general-pies-user"
)

main_page_view = namedtuple(
    "MainPageView",
    [
        "link_skip", "tabs", "collectThings",
        "intervalAsk", "startDetails", "storedName",
        "userDetailsJobResult", "start_note", "disableWhile"
    ]
)(
    "go-to-home", "dashboard-tabs", "collect-session",
    "ask-in-interval", "start-details-fetch-view", "stored-name", "result-for-fetch",
    "Starting Timer...", "disable-while"
)

view_header = namedtuple(
    "ViewHeader",
    [
        "collection", "settings", "askName", "getName", "requestDetails",
        "re_fetch", "genresCount", "studiosCount", "collectionImage", "addUser", "giveName", "appName", "short_name",
        "home", "show_name", "resultForSearch", "validateNote", "collectionTabs", "autoOpen", "autoRun"
    ]
)(
    "view-board-table-details", "view-settings", "ask-user-name", "get-user-name", "request-details",
    "data-descriptive-fetch", "genres-count", "studios-count",
    "https://api.iconify.design/flat-color-icons/database.svg",
    'https://api.iconify.design/ant-design/user-add-outlined.svg?color=darkorange', "give-name", "MyListAnalyzer",
    "MLA",
    "/MLA", "mla-view-show-name", "validate-mal-user-result", "user-validate-check", "view-collection-tabs", "view-collection-open",
    "view-collection-auto-run"
)

dashboard = namedtuple(
    "Dashboard", ["header", "board", "dcc_graph", "tabRefresh", "whenDidRefresh"]
)("header", "board", "core-graph-", "tab-refresh", "tab-refresh-when-view")

view_dashboard = namedtuple(
    "viewDashBoard",
    [
        "collectThings", "userDetailsJobResult", "locationChange", "intervalAsk",
        "startDetails", "tabs", "stop_note", "start_note", "storedName", "startButt", "stopButt", "paging",
        "startButtTrigger", "stopButtTrigger", "fetchStatus", "tempDataStore", "userJobDetailsNote",
        "row_1_colors", "tab_names", "no_data"
    ]
)(
    "view-collect", "view-user-job", "user-view-location", "user-view-ask",
    "start-details-fetch-view", "view-dashboard-tabs",
    "Please Note, When Stopped, we will be deleting everything that was collected before",
    "Starting Timer...", "user-stored-name",
    "https://api.iconify.design/codicon/run-above.svg?color=green",
    "https://api.iconify.design/codicon/run-errors.svg?color=red",
    "view-results-next-page", "start-interval-view", "stop-interval-view", "job-view-status", "job-raw-store-view", "note-user-job-details",
    ["teal", "indigo", "blue", "pink"], ["Overview", "Belts"],
    "https://api.iconify.design/line-md/cloud-off-outline-loop.svg?color=gray"
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

css_classes = namedtuple("CSSClasses", ["jump", "customButton", "home_card", "request_details", "number_counter", "as_percent"])(
    "do-jump", "custom-butt", "home_card", "request-details", "count-number", "percent-number"
)


_status_map = namedtuple(
    "Status", [
        "watching", "plan_to_watch", "completed", "on_hold", "dropped"
    ]
)

status_colors = _status_map("blue", "indigo", "green", "yellow", "red")
status_labels = _status_map("Watching", "Planned to Watch", "Watched", "Paused", "Stopped")


seasons_maps = {
    "winter": ["https://api.iconify.design/game-icons/cold-heart.svg?color=lightblue", "gray"],
    "spring": ["https://api.iconify.design/ph/tree-fill.svg?color=green", "green"],
    "fall": ["https://api.iconify.design/noto/fallen-leaf.svg", "orange"],
    "summer": ["https://api.iconify.design/line-md/sun-rising-filled-loop.svg?color=darkorange", "yellow"]
}
