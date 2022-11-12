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



function requestDetails(perf, _prev, user_name){
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

function enableEmblaForRequestDetails(){
    enable_embla({
        loop: true
      }); // no dragging please
    return window.dash_clientside.no_update;
}


function failedToAskMALAPI(){
    return ddc_link("Repo", "https://github.com/RahulARanger/MyListAnalyzer")
}


function refreshTab(_, label_id){
    animateCounters(label_id?.index);
    enable_embla();

    return say_no(1)[0];
}



async function processUserDetailsWhenNeeded(timer_is_stopped, _index, completed_color, stored, fetched, pipe, user_name, already_fetched, tab_labels){
    const ctx = dash_clientside.callback_context.triggered;
    const said_no = say_no(1)[0];
    if(ctx.length === 0) return said_no;

    const tab_index = _index ?? 0;
    const from_tabs = ctx[0].prop_id.includes("tab");

    if(from_tabs){
        refreshTab(null, tab_labels[tab_index]?.index); // it will be nice to have this 
        // might need some review
    }

    const is_completed = from_tabs ? Boolean(stored) : (timer_is_stopped && completed_color === "green" && fetched.length > 0);
    if(!is_completed) return said_no;

    
    const split_from = already_fetched.length;
    const response_template = {
        failed: true, so: "Unknown, Failed before doing anything.",
        split_from: say_no(split_from)
    }
    

    const ask = new Request(
        `${pipe}/MLA/user_details/process/${tab_index}`,
         {"method": "POST", "body": JSON.stringify({"data": fetched.flat(), "timezone": getTimezone()}), "headers": {"Content-Type": "application/json"}}
        );

    const response = await fetch(ask).then(
        function(response){
            if(!response.ok)
                return Promise.reject(response);
            
            response_template.failed = false;
            response_template.so = "Passed!"
            return response.json();
        }).catch((response) => {
            response_template.so = response.status ? `${response.status} : ${response.statusText}` : ["MAL Server didn't response, Please raise an issue in ", failedToAskMALAPI()]
            return false;
        });

    
    response_template.split_from[tab_index] = response?.meta || said_no;

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
        enableEmblaForRequestDetails,
        processUserDetailsWhenNeeded,
        refreshTab
    }
});
