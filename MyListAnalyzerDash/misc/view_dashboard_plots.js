const view_e_charts_mla = {}; // be a good boy
const pies_for_dist = "pie_dist_overview_mla";
const status_colors = {"Completed": "#90EE90", "Watching": "#87CEEB", "Dropped": "#FFCCCB", "Hold": "#FCE883"}

// // HELPER FUNCTIONS

// UPDATING THEME
fetch('/MLA/assets/theme.json')
  .then(r => r.json())
  .then(theme => {
    echarts.registerTheme('essos', theme);
  });

// USE this if and only if you need to use whole row or column or TABLE
// not for particular cell
class Frame {
  raw;
  constructor(raw) {this.raw = JSON.parse(raw);}
  col(col_index) {return this.raw.map((row) => row[col_index]);}
  row(row_index) {return this.raw[row_index]}
  rows(...indices){return this.raw.map((row) => indices.map((index) => row[index]))}
}

class ConstructEChartOption{
  raw = {}
  light = "rgba(255, 255, 255, 0.3)"
  setTitle(text, size, center, options){
    this.raw.title = { text, textStyle: { fontSize: size }, left: "center", ...(options || {})}; return this;
  }
  setAxis(isX, type, name, showLines, options){
    const option = {type, name, splitLine: { show: showLines }, ...(options || {})};
    if(isX) this.raw.xAxis ? this.raw.xAxis.push(option) : (this.raw.xAxis = [option]);
    else this.raw.yAxis ? this.raw.yAxis.push(option) : (this.raw.yAxis = [option]);
    return this;
  }
  toolBox(hide, mark, magic, hide_restore, hide_save, magic_types){
    const option = {
      show: !hide, feature: {restore: { show: !hide_restore }, saveAsImage: { show: !hide_save } }
    }
    mark && (option.feature.mark = {show: true})
    magic && (option.feature.magicType = {show: true, type: magic_types ? magic_types : ["line", "bar"]})
    this.raw.toolbox = option;
    return this;
  }
  setTooltip(triggeredFor, options){
    this.raw.tooltip = {trigger: triggeredFor, backgroundColor: "#222222", textStyle: {color: "#fff"}, ...(options || {})}  // trigger: item / axis
    return this;
  }
  visualMap(leftText, rightText, min, max){
    this.raw.visualMap = {
      orient: "horizontal", left: "center", min, max, text: [leftText, rightText],
      dimension: 1,
    }
    return this;
  }
  initSeries(){
    this.raw.series = [];
    return this;
  }
  barSeries(data, name, options){
    this.raw.series.push({
      data, type: 'bar', name, ...(options || {})
    }); return this;
  }
  pieSeries(data, name, selectedMode, radius, center){
    this.raw.series.push({
      type: 'pie',
      radius: radius || '65%',
      name,
      center: center || ['50%', '50%'],
      selectedMode: selectedMode || 'multiple',
      data
    }); return this;
  }
  lineSeries(name, data, smooth, options){
    this.raw.series.push({type: "line", name, data, smooth, ...(options || {})}); return this;
  }
  setLegend(data, options, orient, x, type){
    this.raw.legend = { orient: orient || 'horizontal', x: x || 'left', data, type: type || "scroll", ...(options || {})}; return this;
  }
  label(color, labelLineColor, labelLine){
    this.raw.label = {color: color || this.light};
    this.raw.labelLine = {lineStyle: {color: labelLineColor || this.light}, ...(labelLine || {smooth: 0.2, length: 10, length2: 20})}; return this;
  }
  pieEmphasis(){
    this.raw.emphasis = {
      itemStyle: {shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)'}
    }; return this;
  }
  setGrid(containLabel, options){
    this.raw.grid = {containLabel, ...options}; return this;
  }
}


// for creating Echart
function createEChart(id, on) {
  const element = document.getElementById(id);
  if(view_e_charts_mla[id]) disposePlot(view_e_charts_mla[id], element);
  const chart = echarts.init(element, "essos", { renderer: on || 'svg' });
  view_e_charts_mla[id] = chart;
  new ResizeObserver(() => chart.resize()).observe(element);
  return chart
}

// for disposing plots
function disposePlot(plot, element) {
  const save_them = Array(...element.querySelectorAll(".save")).map((e) => {element.removeChild(e); return e;});
  plot?.dispose();
  save_them.forEach((e) => element.appendChild(e));
}


// common toolbox
function generalToolBox() {
  return {
    show: true,
    feature: { mark: { show: true }, magicType: { show: true, type: ['line', 'bar'] }, restore: { show: true }, saveAsImage: { show: true } }
  }
}


function week_js_to_pandas(week_day, otherWay) {
  // pandas say 0 is Monday but for js it is sunday
  if (otherWay) return week_day === 6 ? 0 : (week_day + 1);
  else return week_day ? (week_day - 1) : 6;
}

// // OVERVIEW TAB

function ep_range_dist_plot(data) {
  const values = Object.values(data);
  const keys = Object.keys(data);
  return (new ConstructEChartOption()).initSeries().barSeries(values).setTitle("Range of Anime Episodes", 16, true)
  .setAxis(true, "category", "Episode Range", false, {data: keys, nameLocation: "center", nameGap: 23})
  .setAxis(false, "value", "Freq.", false).setTooltip("axis", {axisPointer: {type: "shadow"}})
  .visualMap("Mostly Seen", "Least Ones", Math.min(...values), Math.max(...values))
  .setGrid(false, {left: 40}).toolBox(false, false, true, true, false).raw;
}


function plotPiesDist(data) {
  const ratings = Object.keys(data);
  const meta_x = ratings.map(function (label) { return { value: data[label], name: label }; });
  const opt = (new ConstructEChartOption()).initSeries().pieSeries(meta_x, "Rating")
  .setTitle("Age Rating Over Animes", 16, true).setTooltip("item", {formatter: "{a} ({c} | {d}%)<br/>{b}"})
  .label().pieEmphasis().toolBox(false, false, false, true).setLegend(ratings, {selected: {TV: false, Unknown: false}}).raw;
  opt.meta_x = meta_x; return opt;
}


function plotForOverviewTab(_, data, page_settings) {
  const no = say_no(1)[0];
  if (!data) return no;

  const ep_range_plot = "ep_dist_overview_mla";
  // DESTROYING PLOTS
  // INIT PLOTS
  const ep_range = createEChart(ep_range_plot);
  ep_range.setOption(ep_range_dist_plot(JSON.parse(data?.ep_range) || {}));

  const dist_pie_plot = createEChart(pies_for_dist);
  const media_dist = JSON.parse(data?.media_dist);
  dist_pie_plot.setOption({meta: Object.keys(media_dist).map((key) => {return {name: key, value: media_dist[key]}}), ...plotPiesDist(JSON.parse(data?.rating_dist) || {})}); dist_pie_plot.setOption({legend: {bottom: 2, left: 130}});
  return no;
}

// // RECENTLY TAB

function weeklyDist(eps_watched_per_week, total_week_days) {
  const max_day = Math.max(...eps_watched_per_week);
  const avg_s = eps_watched_per_week.map((eps_watched, week_index) => {
    const value = eps_watched / total_week_days[week_index];

    eps_watched_per_week[week_index] = eps_watched === max_day ? { value: eps_watched, itemStyle: { color: '#e7a4b6' } } : eps_watched
    return eps_watched === max_day ? { value: value, itemStyle: { color: '#e7a4b6' } } : value
  });

  const itemStyle = { color: "#3d3b72" }
  const onHover = { itemStyle: { color: '#f3cec9' } }
  return (new ConstructEChartOption()).initSeries().barSeries(eps_watched_per_week, "Number of Episodes", {itemStyle, emphasis: onHover})
  .lineSeries("Average", avg_s, true, {yAxisIndex: 1 })
  .setAxis(true, "category", "Week", false, {nameLocation: "middle", data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], axisPointer: {type: "shadow"}, axisTick: {alignWithLabel: true}})
  .setAxis(false, "value", "No. of Eps.", false, {axisLabel: {formatter: "{value} eps"}})
  .setAxis(false, "value", "Eps / Per wk", false, {axisLabel: {formatter: "{value} / wk"}})
  .setGrid(true, {top: 54, left: 10, height: "69%"})
  .setTitle("Weekly Frequency", 14, true)
  .setTooltip("axis", {axisPointer: { type: "shadow" }})
  .toolBox(false, true, false, true).raw;
}


function dailyWeightage(dailyTable) {
  const x = dailyTable.columns.map(function (date) {
    return new Date(Date.parse(`${date[0]}-${date[1]}-${date[2]}`));
  });
  const y = dailyTable?.data[2];
  return (new ConstructEChartOption()).initSeries().lineSeries(
    "Day wise Frequency", y.map((y_, _) => { return [x[_], y_] }), true)
    .setAxis(true, "time", "Date", false)
    .setAxis(false, "value", "Freq.", false).setTooltip("axis").setGrid(false)
    .setTitle("Day Wise Distribution", 14, true).raw;
}


function quickHistory(raw) {
  
  return {
    grid: {
      left: 200
    },
    animationDuration: 1e3,
    animation: true,
    _raw: raw,
    title: {text: "Watch History of the User", left: "center", textStyle: { fontSize: 14 }},
    tooltip: {
      order: "valueDesc",
      trigger: "axis"
    },
    xAxis: {
      // max: 'dataMax',
      splitLine: {
        show: false
      },
    },
    yAxis: {
      type: 'category',
      inverse: true,
       max: 10,
      // axisLine: { show: false },
      // axisLabel: { show: false },
      // axisTick: { show: false },
      splitLine: { show: false },
      },  
    toolbox: {
      show: true,
      feature: { mark: { show: true }, restore: { show: true }, saveAsImage: { show: true } }
    },
    series: [
      {
        name: "Eps. Watched",
        // realtimeSort: true,
        seriesLayoutBy: 'column',
        type: 'bar',
        encode: {
          x: 4,
          y: 1
        },
        itemStyle: {
          color: function (param) {
            return status_colors[param.value[2]] ?? "grey";
          }
        },
        label: {
          show: true,
          position: 'right',
          valueAnimation: true,
          color: "wheat"
        }
      }
    ],
    graphic: {
      elements: [
        {
          type: 'text',
          right: 10,
          top: 40,
          style: {
            text: "...",
            font: '12px monospace',
            fill: '#fff'
          },
          z: 100
        }
      ]
    }
  };  
}



function plotForRecentlyTab(_, data, page_settings, recent_animes) {
  const no = say_no(1)[0];
  if (!data) return no;

  // VALIDATION
  if (!recent_animes) return no;

  // DATA POINTS 
  const frame = new Frame(recent_animes);
  // const stamps = frame.col(5).map((stamp) => new Date(stamp));

  // PLOTS
  const daily_weightage = "daily-weightage"
  const week_plot = "weekly-progress-recently-view";
  const bar_race = "quick-update-history"

  // DESTROYING PLOTS
  // disposePlots(daily_weightage, week_plot, bar_race);

  // INIT PLOTS
  const daily_wise = createEChart(daily_weightage);
  const weekly_plot = createEChart(week_plot);
  const bar_race_plot = createEChart(bar_race);


  daily_wise.setOption(
    dailyWeightage(JSON.parse(data.recently_updated_day_wise || "[]"))
  )

  weekly_plot.setOption(
    weeklyDist(JSON.parse(data.week_dist || "[]"), data.week_days || [])
  );

  bar_race_plot.setOption(quickHistory(frame.rows(0, 1, 2, 3, 4, 5))); // Id, Anime Name, Status, up_until, total

  daily_wise.on("mouseover", function (line_data) {
    const date = line_data.data[0];
    if (!date) return;
    weekly_plot.dispatchAction({ type: "showTip", seriesIndex: 0, dataIndex: week_js_to_pandas(date.getDay()) });
  })

  daily_wise.on("mouseout", function () {
    weekly_plot.dispatchAction({ type: "hideTip" });
  });

  weekly_plot.on("click", { seriesIndex: 0 }, function (bar_data) {
    const selectedDay = week_js_to_pandas(bar_data.dataIndex, true);
    const current_series = daily_wise.getOption().series[0];

    const markers = [];


    current_series.data.forEach((raw) => {
      if (raw[0].getDay() !== selectedDay) return;

      markers.push(
        {
          coord: [raw[0], raw[1]],
          label: { formatter: `${raw[1]}`, color: "#fff" }
        }
      )

    })

    current_series["markPoint"] = { data: markers };
    daily_wise.setOption({ series: [current_series] })
  })

  weekly_plot.on("dblclick", { seriesIndex: 0 }, function (bar_data) {
    // clearing the selected with the double click
    const current_series = daily_wise.getOption().series[0];

    const markers = [];
    current_series["markPoint"] = { data: markers };
    daily_wise.setOption({ series: [current_series] })
  })

  
const template = function(index){
  const raw_option = bar_race_plot.getOption();
  const raw = raw_option._raw;
  if(index >= raw.length) return

  const series_index = 0;
  const series_data = raw_option.series[0].data ?? [];
  
  if(index) raw_option.series[series_index].data = [raw[index], ...series_data.filter((row) => row[0] !== raw[index][0])]
  else raw_option.series[series_index].data = [];
  
  index && (raw_option.graphic[0].elements[0].style.text = new Date(raw[index][5]).toLocaleString());
  bar_race_plot.setOption(raw_option);
  setTimeout(() => template(index + 1), 1e3);
}

template(0);
  return no;
}

function changeThePiesInOverviewTab(for_called){
  const no = say_no(1)[0];
  const chart = view_e_charts_mla[pies_for_dist];
  if(!chart || dash_clientside.callback_context.triggered.length === 0) return no;

  const option = chart.getOption(); const is_rating = for_called === "Rating"; const title = is_rating ? "Age Rating Over Animes" : "Media Type Freq."; const refer = is_rating ? option.meta_x : option.meta;
  option.title[0].text = title; option.legend[0].data = refer.map((obj) => obj.name); option.series[0].data = refer;
  chart.setOption(option); return no;
}


window.dash_clientside = Object.assign({}, window.dash_clientside, {
  "MLAPlots": {
    plotForRecentlyTab,
    plotForOverviewTab,
    changeThePiesInOverviewTab
  }
});

