'use strict';


function malAuthToken(){
    const mal_creds = getCookie("mal-creds");
    if(!mal_creds) return false;
    
    const parsed = JSON.parse(JSON.parse(mal_creds.replace(/\\054/g, ',')));
    return parsed ? `${parsed?.token_type} ${parsed?.access_token}`: false;
}


function animateCounters(tabIndex){
    const class_str = tabIndex ? `.count-number.${tabIndex}` : ".count-number";
    
    Array(...document.querySelectorAll(class_str)).map((x) => animateRawNumbers(x));
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


function refreshTab(_, label_id, soft_refresh){
    enable_swiper_for_view_dashboard(soft_refresh);
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

        refreshTab(null, tab_names[this.tab_index], true);
    }

    async fetchStaticData(
        pipe,
         fetchUserAnimeList, fetchRecentAnimeList,
            userAnimeList, force, alreadyFetchedUserAnimeList, alreadyFetchedRecentAnimeList
        ){
        
        const ok_fetch_user_anime_list = force ? fetchUserAnimeList : !alreadyFetchedUserAnimeList;
        const ok_fetch_recent_anime_list = force ? fetchRecentAnimeList : !alreadyFetchedRecentAnimeList;

        
        const genURL = (end) => `${pipe}/MLA/static/${end}`;
        const no = say_no(1)[0];

        const body = {
            user_name : this.user_name,
            timezone: getTimezone()
        }
        
        const result = [];
        
        // below request is the first request send if needed

        result.push(ok_fetch_user_anime_list ? (await this.__send_request(
            genURL("UserAnimeList"),
            {...body, data: userAnimeList},
        ))?.user_anime_list : no)
        
        result.push(
            this.passed && ok_fetch_recent_anime_list ? (await this.__send_request(
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

    async decide_what_to_fetch(){
        // fetch User Anime List, fetch Recent Anime List
        switch(this.tab_name){
            case true: {
                return [true, true];
            }
            case "Overview": { // overview
                return [true, false];
            }

            case "Recently": { // recently
                return [false, true];
            }
        }
    }
}


async function processUserDetailsWhenNeeded(
        raw_list,
        active_tab,
        ___manually_asked,
        pipe,
        tab_names,
        page_settings,
        parsed_user_anime_list,
        parsed_recent_animes,
        meta_for_tabs){
    // DO NOT WORRY Raw List is not empty if passed
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

    const fetchForStaticDataForFirstTime = ctx[0].prop_id.includes("data");

    // do not refer to the old data if User anime list was fetched again
    if(fetchForStaticDataForFirstTime){
        [parsed_user_anime_list, parsed_recent_animes] = ["", ""];
        meta_for_tabs = meta_for_tabs.map(() => "");
    }
        

    const fetchDynamicData = fetchForStaticDataForFirstTime || !Boolean(meta_for_tabs[processor.tab_index]);

    if(!(fetchDynamicData || fetchForStaticDataForFirstTime))
        return said_no

    const tab_caches = (
        fetchForStaticDataForFirstTime
        ) ? Array(meta_for_tabs.length).fill("") : say_no(meta_for_tabs.length);

    [parsed_user_anime_list, parsed_recent_animes] = await processor.fetchStaticData(
        pipe, ...await processor.decide_what_to_fetch(), raw_list.flat() ?? [], static_index,
        fetchForStaticDataForFirstTime,  
        Boolean(parsed_user_anime_list), Boolean(parsed_recent_animes)
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
    if(!disabled && alert)
        alert.textContent = "you would have to manually search for the user, now";

    return [disabled, required]
}


async function validate_and_fetch_anime_list(
    _, __, ___,
     typedName, modalOpened, pageSettings, location, pipe,
      is_it_for_logged_in_user, bring_nsfw,
      ...disableThem
    ){
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
        error: no,
        rawList: no
    }

    const return_me = () => [
        output_template.closeable, output_template.location, output_template.pageSettings,
        output_template.modalOpened, output_template.show_name, output_template.show_name_url, output_template.error,
        output_template.rawList
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
    const disable = (disabled) => disableThem.forEach((e) => {
        const ele = document.getElementById(e);
        ele && (ele.disabled = disabled);
    })
    disable(true);
    
    let final_user_name = "";
    const result = pageSettings?.disable_user_job ? {result: [[true]], user_name: user_name} : (await fetchRawUserAnimeList(
            pipe, is_it_for_logged_in_user ? "" : user_name, is_it_for_logged_in_user,
            "span[class$='Alert-label']", "div.mantine-Alert-message",
            "button.mantine-Modal-close", bring_nsfw
    ));

    if(result?.failed ?? false){
        output_template.error = result?.why ?? "Disconnected from network connection ?";
    } else{
    if(!result?.result?.at(0)?.length) output_template.error = `${user_name} has empty Anime List`;
    else{
        output_template.rawList = result?.result;
        final_user_name = result?.user_name;}
    }       
    if(typeof output_template.error === "string"){  
        output_template.modalOpened = true;
        disable(false);
        return return_me();
    }
    output_template.closeable = true;
    output_template.location = `${(/(\/MLA\/view[-\w]*)/gm).exec(location)[0]}/${final_user_name}`;
    pageSettings.user_name = final_user_name;
    
    output_template.pageSettings = pageSettings;
    output_template.modalOpened = false;
    output_template.show_name = final_user_name;
    output_template.show_name_url = `https://myanimelist.net/profile/${final_user_name}`;
    
    disable(false);
    return return_me();
}

const swiper_options = {
    time_spent: {
        loop: true,
        grabCursor: true,
        speed: 5e2,
        autoplay: {
            delay: 2.5e3,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
        },
        navigation: {enabled: false},
        slidesPerView: "auto",
        effect: "coverflow",
        on: {
            init: function(){
                animateCounters(); // some clones also needs to be counted
            }
        }
    },
    
    special_belt: {
        loop: true,
        grabCursor: true,
        speed: 10e3,
        autoplay: {
            delay: 0,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
        },
        navigation: {enabled: false},
        slidesPerView: 1,
        spaceBetween: 10,
        freeMode: true,
        breakpoints: {
            3e2: {slidesPerView: 1},
            430: {slidesPerView: 1.25},
            5e2: {slidesPerView: 1.5},
            720: {slidesPerView: 2},
            860: {slidesPerView: 2.5},
            1e3: {slidesPerView: 3},
            12e2: {slidesPerView: 3.5}
        },
        on: {
            init: function(){
                animateCounters();
            }
        }
    },
    currently_airing_cards: {
        loop: true,
        grabCursor: true,
        speed: 5e2,
        autoplay: {
            delay: 2.5e3,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
        },
        navigation: {enabled: false},
        slidesPerView: "auto",
        effect: "cards",
        on: {
            init: function(){
                animateCounters(); // some clones also needs to be counted
            }
        }
    },
    special_belt_for_recent_animes:  {
        loop: true,
        grabCursor: true,
        speed: 10e3,
        autoplay: {
            delay: 0,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
        },
        navigation: {enabled: false},
        slidesPerView: 2,
        spaceBetween: 10,
        freeMode: true,
        breakpoints: {
            3e2: {slidesPerView: 1},
            430: {slidesPerView: 1.25},
            5e2: {slidesPerView: 1.5},
            720: {slidesPerView: 2.5},
            820: {slidesPerView: 1.2},
            1e3: {slidesPerView: 1.5},
            12e2: {slidesPerView: 2}
        }
    }
}



function enable_swiper_for_view_dashboard(soft_refresh){
    document.querySelectorAll(".swiper").forEach(
        function(element){
            if(!element.swiper){
                new Swiper(element, swiper_options[element.id])
                return 
            }
            if(soft_refresh){
                element.swiper.update()
                return;
            }

            element.swiper.destroy(true); // if in case new data is added
            new Swiper(element, swiper_options[element.id]);
        }
    );
}


async function fetchRawUserAnimeList(pipe, user_name, use_token, title, body, closeWhile, is_nsfw){
    const alert_title = document.querySelector(title);
    const alert_body = document.querySelector(body);
    const butt = document.querySelector(closeWhile);

    const old_title = alert_title.textContent;
    const old_body  = alert_body.textContent;
    
    const result = [];
    let book_mark = "";
    const headers = {};
    let why = false;
    let failed = false;
    let final_user_name = "";
    butt && (butt.disabled = true);
    alert_title.textContent = `Fetching Anime List for the User ${user_name}`
    alert_body.textContent = "Preparing Request";
    

    if(use_token)
        headers["token"] = malAuthToken();
    headers["nsfw"] = is_nsfw;

    const incase = async (reason, expected) => {
        why = expected ? (await reason.text()) : reason;
        return true;
    }

    if(use_token){
        // we need to get the user name in case we are fetching the user list by the user name
        const req = new Request(
            `${pipe}/MLA/validateUser`, {method: "GET", headers: headers}
        );

        failed = await fetch(req).then(async (resp) => {
            const ans = await resp.json();
            if(!(resp.ok && ans?.passed)) return Promise.reject(ans?.reason, true);
            
            user_name = ans.user_name;
            alert_body.textContent = "Checking your User Name..."
            
            return false;
        }).catch(incase);
    }

    for(let round = 0; round < 5; round ++){
        if(failed) break;
        
        alert_body.textContent = round === 0 ? `Fetching Animes from the ${user_name}'s list` : `Fetched ${round}k animes, checking if there is even more...`;
        const req = new Request(
            `${pipe}/MLA/fetchUserAnimeList?${new URLSearchParams({url: book_mark, user_name}).toString()}`, {method: "GET", headers: headers}
        );
        const next = await fetch(req).then(async (resp) => {
            const ans = await resp.json();
            if(!(resp.ok && ans?.passed)) return Promise.reject(ans?.reason, true);

            final_user_name = ans.user_name;
            book_mark = ans.next_page;
            
            result.push(ans.raw);
            alert_body.textContent = "Successfully fetched, Checking if there's more."

            return book_mark;

        }).catch((...args) => {failed = true; incase(...args)});

        if(!next) break;
    }

    alert_body.textContent = old_body;
    alert_title.textContent = old_title;
    butt && (butt.disabled = false);

    return failed ? {why, failed} : {user_name: final_user_name, result};
}

function clickToGoCardIndex(_, called_index, swiper_cards_id){
    const no = say_no(1)[0];
    const swiper_obj = document.getElementById(swiper_cards_id)?.swiper;
    if(!swiper_obj) return no;
    
    swiper_obj.slideTo(called_index?.index ?? 0);
    return no;
}


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    "MLA": {
        requestDetails,
        processUserDetailsWhenNeeded,
        refreshTab,
        set_view_url_after_search,
        decide_if_name_required,
        validate_and_fetch_anime_list,
        clickToGoCardIndex
    }
});
