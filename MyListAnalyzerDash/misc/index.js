'use strict';


function decide_refresh_path(isDisabled, tabIndex, prevValues, modified, labels){
    // just save current time in seconds
    const values = replicate_no(prevValues.length);
    
    if(!isDisabled){ return values};
    
    
    const tab_index = Number(tabIndex ?? 0);
    refreshTabs(null, labels[tab_index]);  // only refresh when switching tabs

    
    const current = Number(prevValues[tab_index] ?? -1);
    const now = Number(modified ?? -1);
    // update if the modified time is not same as the recorded ones
    values[tab_index] = current === now ? values[tab_index] : Math.max(current, now);
    return values;
}



function animateCounters(tabIndex){
    Array(...document.querySelectorAll(`.count-number.${tabIndex}`)).map((x) => animateRawNumbers(x));
    return window.dash_clientside.no_update;
}



function refreshTabs(_, tabID){
    const tab_index = tabID?.index;
    animateCounters(tab_index);
    return enablePlainEmbla(tab_index);
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
    animateCounters(label_id?.index);
    enable_embla();

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



async function processUserDetailsWhenNeeded(
    timer_is_stopped,
     _index,
      completed_color,
       stored_user_anime_list, // stored after processing from the raw 
        fresh_raw_fetched, // what it is fetched through the timer
         pipe, // URL for MLA-API
          page_settings,
           purified_tab_data,
            tab_labels  
            ){
    const ctx = dash_clientside.callback_context.triggered;
    const said_no = say_no(1)[0];
    
    // if nobody called you, just DASH called you to know then say "no_update"
    if(ctx.length === 0) return said_no;

    const user_name = page_settings?.user_name ?? "";
    const tab_index = _index ?? 0;
    const from_tabs = ctx[0].prop_id.includes("tab"); // does it because of switching tabs

    const tab_name = tab_labels[tab_index]?.index;
    
    if(from_tabs){
        refreshTab(null, tab_labels[tab_index]); // it will be nice to have this 
        // might need some review if refresh needed for every tab switch
    }

    const is_completed = from_tabs ? !(Boolean(stored_user_anime_list) && Boolean(purified_tab_data[tab_index])) : (timer_is_stopped && completed_color === "green" && fresh_raw_fetched.length > 0);
    // if it is coming because of tabs, then check if you have fetched data before, else check if timer is stopped and process is successful.
    
    if(!is_completed) return said_no;
    // if not completed, then say "no_update"

    
    const split_from = purified_tab_data.length;
    const response_template = {
        failed: true, so: "Unknown, Failed before doing anything.",
        split_from: say_no(split_from)
    }

    const body = {timezone: getTimezone()}

    
    body.data = from_tabs ? stored_user_anime_list : fresh_raw_fetched.flat();

    let response = {};

    if(body.data){
        const ask = new Request(
            `${pipe}/MLA/user_details/process/${tab_name}`,
             {method: "POST", body: JSON.stringify(body), headers: {"Content-Type": "application/json"}}
            );
    
        response = await fetch(ask).then(
            function(response){
                if(!response.ok)
                    return Promise.reject(response);
                
                response_template.failed = false;
                response_template.so = `${tab_name} is now ready.`
                return response.json();
    
            }).catch((response) => {
                response_template.so = response.status ? `${response.status} : ${response.statusText}` : ["MAL Server didn't respond, Please raise an issue in ", failedToAskMALAPI()]
                return false;
            });
    
        
        response_template.split_from[tab_index] = response?.meta || said_no;
    }
    else{
        response_template.failed = true;
        response_template.so = [
            "Request body is empty either because of data is not yet fetched or there was no data for the requested user, else it might be an error.",
             " But either way please ping in  ",
              ddc_link("Repo", "https://github.com/RahulARanger/MyListAnalyzerDash/issues")];
    }

    return [
        response_template.split_from, dmc_notification(
        !response_template.failed,
         response_template.failed ? "red" : "green",
         false, // allow close regardless
         response_template.so,
         `Result for Processing User: ${user_name}'s Details`
        ), response?.drip ? response.drip : said_no
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
