'use strict';

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


function refreshTab(_, label_id){
    enable_splide();
    animateCounters(label_id?.index);
    formatTimers();

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
    tab_settings = [
        [true, false],
        [false, true]
    ];
    // list [tab of] send user details, recent_animes

    response_template = {
        failed: true,
        reason: "Mostly blocked due to CORS Error, or might be backend API is sleeping 😴😴😴.",
        tab_cache: null,
        drip_cache: say_no(1)[0],
        recent_animes_cache: say_no(1)[0]
    };

    tab_index;
    tab_name;
    user_name;

    constructor(tab_index, tab_names, user_name){
        this.tab_index = tab_index ?? 0;
        this.tab_name = tab_names[this.tab_index]?.index;
        this.user_name = user_name;

        refreshTab(null, tab_names[this.tab_index]);
    }

    prepBody(user_details, recent_animes, processAgain){
        const data = {}

        const _set = this.tab_settings[this.tab_index];

        const send_recent_animes = !processAgain && _set[1];
        if(processAgain || _set[0]) data.user_anime_list = user_details;
        if(send_recent_animes) data.recent_animes = recent_animes;

        // if asked to process again, we need to send the raw user anime list regardless of the active tab
        // if asked to process again, we should not send the recent animes regardless of the active tab.
        
        return {
            timezone: getTimezone(),
            user_name: this.user_name,
            data,
            need_to_parse_recent: send_recent_animes
        }
    }

    async sendRequest(pipe, ...args){
        const requestBody = this.prepBody(...args);
        
        const ask = new Request(
            `${pipe}/MLA/user_anime_list/process/${this.tab_name}`,
             {
                method: "POST",
                body: JSON.stringify(requestBody),
                headers: {"Content-Type": "application/json"}
            }
        );
    
        const resp = await fetch(ask).then(
            (response) => {
                if(!response.ok)
                    return Promise.reject(response);

                this.response_template.failed = false;
                return response.json();
    
            }).catch(async (response) => {
                const reason = await response.text();
                this.response_template.reason = reason ? reason : this.response_template.reason;
                return say_no(1)[0];
        });       

        if(resp.drip) this.response_template.drip_cache = resp.drip;
        if(resp.dripped) this.response_template.tab_cache = resp.dripped;
        if(resp.recent_animes) this.response_template.recent_animes_cache = resp.recent_animes;
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
    const asked_to_process_raw = ctx[0].prop_id.includes("disabled"); // does it because of switching tabs

    const processor = new ProcessUserDetails(
        active_tab,
         tab_names,
          page_settings?.user_name ?? ""
    );

    // BUG: yet to find
    const who_triggered = ctx[0].prop_id;
    const ask_to_process = timer_is_stopped && (asked_to_process_raw ? (
        timer_status === "green" && user_anime_list_source.length > 0
    ) : (Boolean(
        parsed_recent_animes
    ) && (
        who_triggered.includes("run-process-job-again") || !Boolean(meta_for_tabs[processor.tab_index])
        )))

    const tab_caches = (
        ask_to_process && asked_to_process_raw
        ) ? Array(meta_for_tabs.length).fill("") : say_no(meta_for_tabs.length);

    if(!ask_to_process){
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

    await processor.sendRequest(
        pipe,
        asked_to_process_raw ? user_anime_list_source.flat() : parsed_user_anime_list,
        parsed_recent_animes,
        asked_to_process_raw
    );

    
    tab_caches[processor.tab_index] = processor.response_template.tab_cache;
    
    const message = [processor.response_template.reason];
    if(processor.response_template.failed)
        message.push(
            ". Reasonable Issue ? then log it in ",
            ddc_link("Issues.", "https://github.com/RahulARanger/MyListAnalyzerDash/issues")
        )

    const note = processor.response_template.failed ? dmc_notification(
        false, // autoClose
        processor.response_template.failed ? "red" : "green",
        false,
        message,
        `Result for Processing User: ${processor.user_name}'s Details`
    ) : said_no;
    // if passed, do not show notification, to reduce the traffic.
    

    return [
        tab_caches,
        note,
        processor.response_template.drip_cache,
        processor.response_template.recent_animes_cache,
        said_no
    ]
}



window.dash_clientside = Object.assign({}, window.dash_clientside, {
    "MLA": {
        requestDetails,
        processUserDetailsWhenNeeded,
        refreshTab,
        set_view_url_after_search
    }
});
