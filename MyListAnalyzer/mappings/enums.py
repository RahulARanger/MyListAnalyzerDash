from collections import namedtuple

askName = namedtuple("AskName", [
    "askName", "getName", "backToView", "search", "note", "resultForSearch",
])(
    "ask-name", "getName", "back-to-view",
    "https://api.iconify.design/flat-color-icons/search.svg",
    "Enter valid user name whose status was set to public. but do note that if either user name was invalid or status "
    "was not set to public. You will be asked to enter the username again",
    "result-for-search")

main_app = namedtuple("MainApplication", [
    "loadApp", "loadingProps", "about", "repo", "body", "me"
])(
    "__app_load", {"variant": "bars", "color": "orange", "size": "xl"},
    "_about_mal-r", "https://github.com/RahulARanger/MyListAnalyzer", "dashboard-body", "logged-in-user"
)

home_page = namedtuple("HomePage", [
    "url", "name", "description", "github_logo", "tests", "testID", "testResult", "greet", "testNote", "testFilter",
    "testIcon", "apps"
])(
    "/MLA/", "Home", "Home Page of the MyListAnalyzer, please check the Test Cases tab",
    "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", [
        "Logged in MAL", "Are MAL Tokens valid ?"], "test", "test-area", "Allow MyListAnalyzer to access your,",
    "test-results", "test-filter", "https://api.iconify.design/carbon/rule-test.svg", [
        ["View Dashboard", "/view/", "Dashboard for MyAnimeList Users"]
    ]
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
    ["collection", "settings", "askName", "getName", "requestDetails", "re_fetch", "genresCount", "studiosCount"]
)(
    "view-board-table-details", "view-settings", "ask-user-name", "get-user-name", "request-details",
    "data-descriptive-fetch", "genres-count", "studios-count"
)

dashboard = namedtuple(
    "Dashboard", ["header", "board", "dcc_graph", "tabRefresh", "whenDidRefresh"]
)("header", "board", "core-graph-", "tab-refresh", "tab-refresh-when-view")

view_dashboard = namedtuple(
    "viewDashBoard",
    [
        "collectThings", "userDetailsJobResult", "locationChange", "intervalAsk",
        "startDetails", "tabs", "stop_note", "start_note", "storedName"
    ]
)(
    "view-collect", "view-user-job", "user-view-location", "user-view-ask",
    "start-details-fetch-view", "view-dashboard-tabs",
    "Please note, you will seeing the results of the limited data, please view the Data Collection, to see how much "
    "was collected",
    "Starting Timer...", "user-stored-name"
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

css_classes = namedtuple("CSSClasses", ["jump", "customButton", "home_card"])(
    "do-jump", "custom-butt", "home_card"
)
