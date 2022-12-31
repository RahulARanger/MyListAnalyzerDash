'use strict';


function malAuthToken(){
    const mal_creds = getCookie("mal-creds");
    if(!mal_creds) return false;
    
    const parsed = JSON.parse(JSON.parse(mal_creds.replace(/\\054/g, ',')));
    return parsed ? `${parsed?.token_type} ${parsed?.access_token}`: false;
}


function animateCounters(tabIndex){
    Array(...document.querySelectorAll(`.count-number.${tabIndex}`)).map((x) => animateRawNumbers(x));
    return window.dash_clientside.no_update;
}


function formatTimers(){
    document.querySelectorAll(".need_to_time_format").forEach(
        (e) => new FormattedTimeElement(e)
    );
}


function requestDetails(perf, _prev, page_settings){
    const user_name = page_settings?.user_name ?? "";
    
    if(!perf) return say_no(1)[0];

    const previous = structuredClone(_prev);
    const traces = previous?.data;

    perf.called = formateTime(perf?.called);
    
    if(!traces.length)
        previous.data =  [{
            'line': {'color': 'orange', 'shape': 'spline'},
             'mode': 'lines+markers',
              'x':  [perf?.called], 'y': [perf?.taken],
               'type': 'scatter'
        }]
        
    else{
        traces[0]?.x.push(perf?.called);
        traces[0]?.y.push(perf?.taken);
    }


    return previous;
}

function failedToAskMALAPI(){
    return ddc_link("Repo", "https://github.com/RahulARanger/MyListAnalyzer")
}

function setColorBasedOnRankParser(){
    document.querySelectorAll(".format_rank_index").forEach(setColorBasedOnRank);
}


function refreshTab(_, label_id){
    enable_splide();
    animateCounters(label_id?.index);
    formatTimers();
    setColorBasedOnRankParser();

    return say_no(1)[0];
}


function set_view_url_after_search(page_settings, url){
    const user_name = page_settings?.user_name ?? "";
    const url_regex = new RegExp("\/MLA\/view([a-z\-].)?");
    const result = url_regex.exec(url);

    const final_result = result ? `${result[0]}/${user_name}` : `/MLA/view/${user_name}`
    
    return [
        Boolean(user_name),
        final_result,
        user_name,
        `https://myanimelist.net/profile/${user_name}`
    ]
}


class ProcessUserDetails{
    reason = "Mostly blocked due to CORS Error, or might be backend API is sleeping 😴😴😴.";
    tab_index = 0;
    tab_name;
    user_name;
    passed = true;

    constructor(tab_name, tab_names, user_name){
        for(const [index, tab_format] of tab_names.entries())  if(tab_format?.index === tab_name){ this.tab_index = index; break;}
        
        this.tab_name = tab_name;
        this.user_name = user_name;

        refreshTab(null, tab_names[this.tab_index]);
    }

    async fetchStaticData(
        pipe,
         fetchUserAnimeList, fetchRecentAnimeList,
            userAnimeList
        ){
        const genURL = (end) => `${pipe}/MLA/static/${end}`;
        const no = say_no(1)[0];

        const body = {
            user_name : this.user_name,
            timezone: getTimezone()
        }
        
        const result = [];
        
        // below request is the first request send if needed

        result.push(fetchUserAnimeList ? (await this.__send_request(
            genURL("UserAnimeList"),
            {...body, data: userAnimeList},
        ))?.user_anime_list : no)
        
        result.push(
            this.passed && fetchRecentAnimeList ? (await this.__send_request(
                genURL("RecentAnimeList"),
                body
            ))?.recent_animes : no
        );

        return result;
    }


    async fetchDynamicData(pipe, data){
        const url = `${pipe}/MLA/dynamic/${this.tab_name}`;

        const body = {data, user_name: this.user_name, timezone: getTimezone()};
        
        switch (this.tab_name) {
            case "Overview":
                return this.__send_request(
                    url, body
                );
            case "Recently": 
                return this.__send_request(
                    url, body
                )
        }       

    }

    async __send_request(url, body){
        const req = new Request(
            url, {method: "POST", body: JSON.stringify(body), headers: {"Content-Type": "application/json"}}
        );


        return fetch(req).then(
            (response) => {
                if(!response.ok)
                    return Promise.reject(response);

                this.passed = true && this.passed;
                return response.json();
            }).catch(async (response) => {
                try{
                    const reason = await response.text();
                    this.reason = reason ? reason : this.reason;
                }
                catch{
                    this.reason = "Failed, Because API got stuck with something it can't understand. I was waiting for such errors."
                }

                this.passed = false;

                return say_no(1)[0];
        });       
    }

    async extractData(userAnimeList, recentAnimeList){
        switch (this.tab_name) {
            case "Overview":
                return userAnimeList;
            case "Recently":
                 return recentAnimeList;
        }
    }

    async decide_what_to_fetch(static_index){
        // fetch User Anime List, fetch Recent Anime List
        switch(static_index){
            case true: {
                return [true, true];
            }
            case 0: { // overview
                return [true, false];
            }

            case 1: { // recently
                return [false, true];
            }
        }
    }
}


async function processUserDetailsWhenNeeded(
        timer_is_stopped,
        active_tab,
        ___manually_asked,
        timer_status,
        pipe,
        tab_names,
        page_settings,
        user_anime_list_source,
        parsed_user_anime_list,
        parsed_recent_animes,
        meta_for_tabs){

    const ctx = dash_clientside.callback_context.triggered;
    const said_no = say_no(1)[0];    
    // if nobody called you, then say "no_update"
    if(ctx.length === 0) return said_no;

    const processor = new ProcessUserDetails(
        active_tab,
         tab_names,
          page_settings?.user_name ?? ""
    );


    // decide for which will we have to fetch static and dynamic data
    const static_index = true; // means all

    const timer_was_called = ctx[0].prop_id.includes("disabled");
    const timer_was_called_when_disabled = timer_was_called && timer_is_stopped;
    
    const fetchForStaticDataForFirstTime = [
        timer_was_called_when_disabled,
         timer_status === "green",
         user_anime_list_source.length > 0
    ].every((x) => x);

    if(fetchForStaticDataForFirstTime)
        switch(static_index){
            case true:{
                meta_for_tabs = meta_for_tabs.map(() => "");
            }
        }

    const fetchDynamicData = (timer_was_called ? timer_was_called_when_disabled : true) && !Boolean(meta_for_tabs[processor.tab_index]);

    const tab_caches = (
        fetchForStaticDataForFirstTime
        ) ? Array(meta_for_tabs.length).fill("") : say_no(meta_for_tabs.length);

    if(!(fetchDynamicData || fetchForStaticDataForFirstTime)){
        const send_note = user_anime_list_source.length === 0 && timer_is_stopped && timer_status === "green";
        if(!send_note) return said_no;
        
        else return [
            tab_caches,
            dmc_notification(
                false,
                "red",
                false,
                `Requested User: ${processor.user_name} has empty anime list. Please request for other user.`,
                `Empty Anime List`
            ),
            said_no,
            said_no
        ]
    }

    if(fetchForStaticDataForFirstTime)
        [parsed_user_anime_list, parsed_recent_animes] = await processor.fetchStaticData(
            pipe, ...await processor.decide_what_to_fetch(static_index), user_anime_list_source.flat(), static_index
        );

    if(processor.passed && fetchDynamicData){
        const asked = await processor.extractData(
            parsed_user_anime_list, parsed_recent_animes
        );
        
        if(asked)
            tab_caches[processor.tab_index] = await processor.fetchDynamicData(pipe, asked);
    }
    
    const message = [processor.reason];
    if(!processor.passed)
        message.push(
            ". Reasonable Issue ? then log it in ",
            ddc_link("Issues.", "https://github.com/RahulARanger/MyListAnalyzerDash/issues")
        )

    const note = !processor.passed ? dmc_notification(
        false, "red", false, message,
        `Result for Processing User: ${processor.user_name}'s Details`
    ) : said_no;
    // if passed, do not show notification, to reduce the traffic.
    
    const stores = processor.passed ? [
        parsed_user_anime_list, parsed_recent_animes
    ] : say_no(2)

    return [
        tab_caches,
        note,
        ...stores,
        said_no
    ]
}


function decide_if_name_required(is_it_on){
    if(is_it_on === undefined) return say_no(1)[0];
    const required = !is_it_on;
    const disabled = is_it_on;
    const alert = document.querySelector('div.mantine-Text-root[role="alert"]');
    if(disabled && alert) {
        const p = document.createTextNode("You can now directly search for the user, given you are logged in else you can now login from ");
        const a = document.createElement("a");
        a.href = "/MLA";
        a.textContent = "here"
        alert.textContent = ""

        alert.appendChild(p); alert.appendChild(a)
    }
    else alert.textContent = "you would have to manually search for the user, now";

    return [disabled, required]
}


async function validate_user(_, __, ___, typedName, modalOpened, pageSettings, location, pipe, doNotInterrupt, inputID, is_it_for_logged_in_user){
    const ctx = dash_clientside.callback_context.triggered;
    const who_triggered_it = ctx.length === 0 ? "" : ctx[0].prop_id;

    const no = say_no(1)[0];

    const user_name = who_triggered_it ? typedName : pageSettings?.user_name;
    
    const output_template = {
        closeable: no,
        location: no,
        pageSettings: no,
        modalOpened: no,
        show_name: no,
        show_name_url: no,
        error: no
    }

    const return_me = () => [
        output_template.closeable, output_template.location, output_template.pageSettings,
        output_template.modalOpened, output_template.show_name, output_template.show_name_url, output_template.error
    ];

    if(who_triggered_it.includes("search_user_name_view")){
        output_template.modalOpened = !modalOpened;
        return return_me();
    }
    
    const passed = is_it_for_logged_in_user || /^\w+$/g.test(user_name);

    if(!passed){
        
        output_template.modalOpened = true;
        output_template.closeable = false;
        output_template.error = user_name ? "Expecting only alphabetic characters in user name." : "Please Enter User Name";
        return return_me();
    }

    const disable = (disabled) => [doNotInterrupt, inputID].forEach((e) => {
        const ele = document.getElementById(e);
        ele && (ele.disabled = disabled);
    })

    disable(true);

    const headers = {'Content-Type': 'application/json'}
    const body = {user_name}
    
    if(is_it_for_logged_in_user){
        headers["token"] = malAuthToken();
        body.user_name = "";
    }
    
    const req = new Request(`${pipe}/MLA/validate_user`, {method: "POST", body: JSON.stringify(body), headers: headers})
    
    const final_user_name = await fetch(req).then(async (resp) => {
        const ans = await resp.json();
        if(!(resp.ok && ans?.passed)) return Promise.reject(ans?.reason, true);
        return ans.user_name;
    }).catch(async (reason, expected) => {
        output_template.error = expected ? (await reason.text()) : reason;
        return ""
    }) || user_name;


    
    if(typeof output_template.error === "string"){
        output_template.modalOpened = true;
        disable(false);
        return return_me();
    }

    output_template.closeable = true;
    output_template.location = `/MLA/view/${final_user_name}`;
    pageSettings.user_name = final_user_name;
    
    output_template.pageSettings = pageSettings;
    output_template.modalOpened = false;
    output_template.show_name = final_user_name;
    output_template.show_name_url = `https://myanimelist.net/profile/${final_user_name}`;
    
    disable(false);
    return return_me();
    
    // document.getElementById(search_bar_id).textContent = actual_user_name;
}

function fetch_raw_user_anime_list() {
    // TODO: migrate fetch raw user anime list from python to javascript
}



window.dash_clientside = Object.assign({}, window.dash_clientside, {
    "MLA": {
        requestDetails,
        processUserDetailsWhenNeeded,
        refreshTab,
        set_view_url_after_search,
        decide_if_name_required,
        validate_user
    }
});
