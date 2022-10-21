'use strict';

const mal_username_test = new RegExp(/^\w+$/);;


// UTILS FUNCTIONS
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}


function formatDate(from_epoch){
    const date = new Date(Number(from_epoch) * 1000);
    return `${date.getMonth()+1}/${date.getDate()}/${date.getFullYear()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')} ${date.getHours() > 12 && date.getMinutes() >= 0 ? 'PM' : 'AM'}`;
}

function randomIntFromInterval(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min)
}

const colors = ["dark", "gray", "red", "pink", "grape", "violet", "indigo", "blue", "cyan", "teal", "green", "lime", "yellow", "orange"]

function randomColor(..._){
    return colors[Math.floor(Math.random(colors.length) + 1)];
}



function decide_modal(n_clicks, opened){
    if(n_clicks === undefined){
        return false;
    }
    return !Boolean(opened);
}

function formatTimeInComp(value){return value ? formatDate(value) : "--"}

function handleShimmer(figure){
    return !Boolean(figure.data[0].values);
}


function handleTests(checks, currentCodes){
    // checks is the list of checks for the checkboxes: passed, fail, unknown
    // currentCodes is the list of colors of the current badges
    // returns whether to hide or not
    const currentMapped = {green: checks[0], red: checks[1], yellow: checks[2]}
    
    return currentCodes.map(function(result){
        return {display: currentMapped[result] ? "initial" : "none"}
    })
}


function invalidToDisable(_, check_id){
    const element = document.getElementById(check_id);
    return !(element ? element.checkValidity() : Boolean(_))
}


function toSearch(_){
    if(!_) return window.dash_clientside.no_update;
    
    return "/_ask_name";
}

function diffTimeMinutes(past, newThings){
    const left = newThings ?? new Date();
    return Math.abs(left - past) / 6e4;
}

function replicate_no(times){
    return Array(times).fill(window.dash_clientside.no_update);
}


function startCollection(storedName, is_it_me){
    // we are using round about way in order to implement some scripts in future
    return [
        storedName ? storedName : window.dash_clientside.no_update,
         storedName ? (is_it_me ? "orange" : "blue") : "gray",
         `/view/${storedName}`
    ]
    
}



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

function compareAndRefresh(refresh, current_tab, rates){
    const now = new Date();

    if(now === rates[current_tab]){
        return window.dash_clientside.no_update;
    }

    return [...replicate_no(current_tab - 1), now, ...replicate_no(current_tab + 1)];
}


function getTimezone(){
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}



function handleChecks(_checks){
    const checks = _checks.map((x) => x ?? true);
    // checks are for not allowing user to disable both the checkboxes (genres, studios)
    const all_checked = checks.every(Boolean);
    return [!all_checked]
}


function enterToClick(_, textID, buttonID){
    const element = document.getElementById(textID);
    if(element.checkValidity()) document.getElementById(buttonID).click();
    return window.dash_clientside.no_update;
}

function animateRawNumbers(number){
    const maxi = Number.parseFloat(number.textContent);
    const isInt = Number.isInteger(maxi);
    const isPercent = number.textContent.at(-1) === "%";
    
    let startFrom = 0;
    
    const increment = isPercent ? 0.69 : (maxi < 100 ? 1 : 6);
    const once = (
        isInt ? String(Number((isPercent ? number.textContent.slice(0, -1) : number.textContent))
        ) : String(maxi.toFixed(2))).length;
    number.title = `${maxi}${isPercent ? '%' : ''}`

    const id_ = setInterval(function(){
        number.textContent = `${isInt ? startFrom : startFrom.toFixed(2)}${isPercent ? '%' : ''}`.padStart(once, "0");
        if(startFrom === maxi) clearInterval(id_);
        startFrom += Math.min(maxi - startFrom, increment);

    }, 30)
}


function animateCounters(tabIndex){
    Array(...document.querySelectorAll(`.count-number.${tabIndex}`)).map((x) => animateRawNumbers(x));
    return window.dash_clientside.no_update;
}

function enablePlainEmbla(tabIndex) { 
    
    Array(...document.querySelectorAll(`.${tabIndex}.embla`)).forEach(function(wrap){
        const viewPort = wrap.querySelector(".embla__viewport");
        const prevBtn = wrap.querySelector(".embla__button--prev");
        const nextBtn = wrap.querySelector(".embla__button--next");
        const embla = EmblaCarousel(viewPort, { loop: true });
    });

    return window.dash_clientside.no_update;
}


function refreshTabs(_, tabID){
    const tab_index = tabID?.index;
    animateCounters(tab_index);
    return enablePlainEmbla(tab_index);
}


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    modal:{
        decide_modal
    },

    handleData: {
        startCollection,
        formatTimeInComp,
        handleShimmer,
        handleTests,
        randomColor,
        getTimezone,
        handleChecks
    },
    
    redirectThings: {
        toSearch
    },

    tabCache: {
        decide_refresh_path,
        compareAndRefresh
    },
    eventListenerThings: {
        invalidToDisable,
        enterToClick,
        refreshTabs
    }
});
