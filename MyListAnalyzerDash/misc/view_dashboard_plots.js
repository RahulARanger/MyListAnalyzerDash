const week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const recently_e_charts = {}; // be a good boy

function parseWeeksFromStamps(stamps){
    const week_freq = {};
    stamps.forEach(_ => {
        const element = week_days[_.getDay()];
        week_freq[element] = (week_freq[element] || 0) + 1;
    });

    const max_value = Math.max(...Object.values(week_freq))

    const itemStyle = {color: "#3d3b72"}
    const onHover = {itemStyle: {color: '#f3cec9'}}

    return {
        tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
        title: {text: "Weekly Frequency", top: "90%", right: "0%"},
        grid: {top: '20%', containLabel: true, left: "5%"},
        xAxis: {data: week_days, axisTick: {alignWithLabel: true}},
        yAxis: {splitLine: {show: false}},
        series: [
          {
            type: 'bar',
            name: "Number of Episodes",
            data: week_days.map((day) => week_freq[day] === max_value ? {value: week_freq[day], itemStyle: {color: '#e7a4b6'}} : week_freq[day]),
            itemStyle , emphasis:onHover
          }
        ],
        aria: {enabled: true},
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                magicType: {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        }
      };
}


function createEChart(element, on){
    const article = document.createElement("article");
    article.id = element.id + "-article"
    element.appendChild(article);

    const chart = echarts.init(article, null, { renderer: on || 'svg' });
    new ResizeObserver(() => chart.resize()).observe(article);
    return chart
}


function plotForRecentlyTab(_, data, page_settings){
    const no = window.dash_clientside.no_update;
    
    if(!data) return no;
    
    // VALIDATION
    const _stamps = Object.values(JSON.parse(data["stamps"]));
    if(!_stamps) return no;
    
    
    // DATA POINTS 
    const stamps = _stamps.map((stamp) => new Date(stamp * 1e3));
    
    // DESTROYING PLOTS
    const week_plot = "weekly-progress-recently-view"; 
    recently_e_charts[week_plot]?.dispose();

    // INIT PLOTS
    const weekly_plot = createEChart(document.getElementById(week_plot));
    weekly_plot.setOption(parseWeeksFromStamps(stamps));
    
    // SAVING PLOTS
    recently_e_charts[week_plot] = weekly_plot;

    window.addEventListener("resize", function(){
        weekly_plot.resize();
    });

    return no;
}


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    "MLAPlots": {
        plotForRecentlyTab
    }
});

