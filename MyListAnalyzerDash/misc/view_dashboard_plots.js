const week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const view_e_charts_mla = {}; // be a good boy

// UPDATING THEME
fetch('/MLA/assets/theme.json')
  .then(r => r.json())
  .then(theme => {
    echarts.registerTheme('essos', theme);
});


window.addEventListener('resize', function(){
  Object.values(view_e_charts_mla).forEach((plot) => plot?.resize());
});



// USE this if and only if you need to use whole row or column or TABLE
// not for particular cell
class Frame{
    raw;
    constructor(raw){
        this.raw = JSON.parse(raw);
    }

    col(col_index){
        return this.raw.map((row) => row[col_index]);
    }

    row(row_index){
        return this.raw[row_index]
    }
}



function createEChart(element, on){
  const chart = echarts.init(element, "essos", { renderer: on || 'svg' });
  new ResizeObserver(() => chart.resize()).observe(element);
  return chart
}

function displayPlots(...plots){
  plots.forEach((plot) => view_e_charts_mla[plot]?.dispose());
}

function generalToolBox(){
  return {
    show : true,
    feature : {mark : {show: true},magicType: {show: true, type: ['line', 'bar']},restore : {show: true},saveAsImage : {show: true}}}
}



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
        xAxis: {data: week_days, axisTick: {alignWithLabel: true}, splitLine: {show: false}},
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
        toolbox: generalToolBox()
      };
}


function plotForRecentlyTab(_, data, page_settings, recent_animes){
    const no = say_no(1)[0];
    if(!data) return no;
    
    // VALIDATION
    if(!recent_animes) return no;

    // DATA POINTS 
    const frame = new Frame(recent_animes);
    const stamps = frame.col(5).map((stamp) => new Date(stamp));
    
    // DESTROYING PLOTS
    const week_plot = "weekly-progress-recently-view"; 
    displayPlots(week_plot);

    // INIT PLOTS
    const weekly_plot = createEChart(document.getElementById(week_plot));
    weekly_plot.setOption(parseWeeksFromStamps(stamps));
    
    // SAVING PLOTS
    view_e_charts_mla[week_plot] = weekly_plot;
    return no;
}


function ep_range_dist_plot(data){
  const values = Object.values(data);
  const keys = Object.keys(data);

  return {
    tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
    title: {text: "Range of Anime Episodes", left: "center", textStyle: {fontSize: 16}},
    xAxis: {type: "category", data: keys, splitLine: {show: false}, name: "Episode Range"},
    yAxis: {type: "value", splitLine: {show: false}, name: "Anime Count"},
    visualMap: {
      orient: "horizontal", left: "center", min: Math.min(...values), max: Math.max(...values),
      text: ["Mostly Seen", "Least ones"],
      dimension: 1,
    },
    series: [{
        data: values,
        type: "bar"}],
    toolbox: generalToolBox()
  };
  
}


function plotRatingsDist(data){
    const ratings = Object.keys(data);

    return {
      title: {text: "Age Rating over Animes", top: "90%", left: "center", textStyle: {fontSize: 16}},
        legend: {orient: 'horizontal', x: 'left', data: ratings, type: "scroll"},
        tooltip: {trigger: "item", formatter: "{a} ({c} | {d}%)<br/>{b}"},
        series: [
          {
            type: 'pie',
            radius: '65%',
            name: "Rating",
            center: ['50%', '50%'],
            selectedMode: 'multiple',
            data: ratings.map(function(label){return {value: data[label], name: label};})
          }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          color: "rgba(255, 255, 255, 0.3)"
        },
        labelLine: {
          lineStyle: {
            color: "rgba(255, 255, 255, 0.3)"
          },
          smooth: 0.2,
          length: 10,
          length2: 20
        },
        animationType: "scale",
        toolbox: {show : true, feature : {saveAsImage : {show: true}}}
      };
}


function plotForOverviewTab(_, data, page_settings){
    const no = say_no(1)[0];
    if(!data) return no;

    const ep_range_plot = "ep_dist_overview_mla"
    const rating_plot = "rating_dist_overview_mla";
    
    // DESTROYING PLOTS
    displayPlots(ep_range_plot, rating_plot);

    // INIT PLOTS
    const ep_range = createEChart(document.getElementById(ep_range_plot));
    ep_range.setOption(ep_range_dist_plot(JSON.parse(data?.ep_range) || {}))
    
    const ratings_dist = createEChart(document.getElementById(rating_plot));
    ratings_dist.setOption(plotRatingsDist(JSON.parse(data?.rating_dist) || {}));
    
    // SAVING PLOTS
    view_e_charts_mla[ep_range_plot] = ep_range;
    view_e_charts_mla[rating_plot] = ratings_dist;
    return no;
}



window.dash_clientside = Object.assign({}, window.dash_clientside, {
    "MLAPlots": {
        plotForRecentlyTab,
        plotForOverviewTab
    }
});

