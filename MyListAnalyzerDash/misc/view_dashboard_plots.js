const theme = ["inspired", "cool"][Math.floor(Math.random() * 2)];
const script = document.createElement('script');
script.type = 'text/javascript'; script.src = `https://cdn.jsdelivr.net/npm/echarts@5.4.1/theme/${theme}.min.js`;
document.querySelector("head").appendChild(script);

const view_e_charts_mla = {}; // be a good boy
const pies_for_dist = "pie_dist_overview_mla";
const status_colors = {"Completed": "#90EE90", "Watching": "#87CEEB", "Dropped": "#FFCCCB", "On Hold": "#FCE883"}
const week_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

// // HELPER FUNCTIONS
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
    this.raw.title = { text, textStyle: { fontSize: size, color: "#fffffd"}, left: center, ...(options || {})}; return this;
  }
  setAxis(isX, type, name, showLines, options){
    const option = {type, name, splitLine: { show: showLines }, textStyle: {color: "#fffffd"}, ...(options || {})};
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
      dimension: 1, textStyle: {color: "#fffffd"}
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
  pieSeries(data, name, selectedMode, radius, center, options){
    this.raw.series.push({
      type: 'pie', radius: radius || '65%', name,
      center: center || ['50%', '50%'], selectedMode: selectedMode || 'multiple', data, ...(options || {})
    }); return this;
  }
  lineSeries(name, data, smooth, options){
    this.raw.series.push({type: "line", name, data, smooth, ...(options || {})}); return this;
  }
  scatterSeries(data, name, ptExtendSize, options){
    this.raw.series.push({name, type: 'scatter', data, symbolSize: function (dataItem) {return dataItem[1] * (ptExtendSize || 20);}, ...(options || {})}); return this; 
  }
  setLegend(data, options, orient, x, type){
    this.raw.legend = { orient: orient || 'horizontal', x: x || 'left', data, type: type || "scroll", inactiveColor: "#333", textStyle: {color: "#fffffd"}, ...(options || {})}; return this;
  }
  picBarSeries(data, symbol, z, options){
    this.raw.series.push(
      {type: "pictorialBar", symbol, symbolRepeat: 'fixed', symbolMargin: '5%', symbolClip: true,  symbolSize: 20, data, z, ...(options || {})}
    ); return this;
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
  setDataSet(options){
    this.raw.dataset = options; return this;
  }
}
// for creating Echart
function createEChart(id, on) {
  const element = document.getElementById(id);
  if(view_e_charts_mla[id]) disposePlot(view_e_charts_mla[id], element);
  const chart = echarts.init(element, theme, { renderer: on || 'svg' });
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
  return (new ConstructEChartOption()).initSeries().barSeries(values).setTitle("Range of Anime Episodes", 16, "2px")
  .setAxis(true, "category", "Episode Range", false, {data: keys, nameLocation: "center", nameGap: 23})
  .setAxis(false, "value", "Freq.", false).setTooltip("axis", {axisPointer: {type: "shadow"}})
  .visualMap("Mostly Seen", "Least Ones", Math.min(...values), Math.max(...values))
  .setGrid(false, {left: 40}).toolBox(false, false, true, true, false).raw;
}


function plotPiesDist(dataset) {
  const _ratings = dataset[0].source; const ratings = []; const _media = dataset[1].source;
  dataset[0].source = Object.keys(_ratings).map((key) => {ratings.push(key); return {name: key, value: _ratings[key]}}),
  dataset[1].source = Object.keys(_media).map((key) => {return {name: key, value: _media[key]}})
  return (new ConstructEChartOption()).initSeries().setDataSet(dataset).pieSeries(null, "Rating", null, null, null, {datasetIndex: 0})
  .setTitle ("Age Rating Over Animes", 16, true).setTooltip("item", {formatter: (params) =>  `<b>${params.seriesName}:</b> ${params.value.name}<br>${params.percent}% | ${params.value.value}`})
  .label().pieEmphasis().toolBox(false, false, false, true).setLegend(ratings, {selected: {TV: false, Unknown: false}}).setGrid(true, {top: 15}).raw;
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
  dist_pie_plot.setOption(
    plotPiesDist([
      {id: "Age Rating over Animes", source: JSON.parse(data?.rating_dist), name: "Rating"},
      {id: "Media Types of Animes", source: JSON.parse(data?.media_dist) || {}, name: "Media Type"}
    ])); dist_pie_plot.setOption({legend: {bottom: 2, left: 130}});
  return no;
}

// // RECENTLY TAB

function weeklyDist(eps_watched_per_week, total_week_days) {
  const max_day = Math.max(...eps_watched_per_week);
  const avg_s = eps_watched_per_week.map((eps_watched, week_index) => {
    const value = (eps_watched / total_week_days[week_index]).toFixed(2);

    eps_watched_per_week[week_index] = eps_watched === max_day ? { value: eps_watched, itemStyle: { color: '#e7a4b6' } } : eps_watched
    return eps_watched === max_day ? { value: value, itemStyle: { color: '#e7a4b6' } } : value
  });

  const itemStyle = { color: "#3d3b72" }
  const onHover = { itemStyle: { color: '#f3cec9' } }
  return (new ConstructEChartOption()).initSeries().barSeries(eps_watched_per_week, "Number of Episodes", {itemStyle, emphasis: onHover})
  .lineSeries("Average", avg_s, true, {yAxisIndex: 1 })
  .setAxis(true, "category", "Week", false, {nameLocation: "middle", nameGap: 23, data: week_names, axisPointer: {type: "shadow"}, axisTick: {alignWithLabel: true}})
  .setAxis(false, "value", "No. of Eps.", false, {axisLabel: {formatter: "{value} eps"}})
  .setAxis(false, "value", "Eps / Per wk", false, {axisLabel: {formatter: "{value} / wk"}})
  .setGrid(true, {top: 54, left: 10, height: "63%"})
  .setTitle("Weekly Frequency", 14, true)
  .setTooltip("axis", {axisPointer: { type: "shadow" }})
  .toolBox(false, true, false, true).raw;
}


function dailyWeightage(dailyTable) {
  // do not consider time else diff in days will be wrong while rounding off.
  const today = new Date(new Date().toDateString()); const today_s_date = today.getDate();
  const past_14_days = Array(15).fill(true).map((_, index) => [new Date(new Date().setDate(today_s_date - index)), 0]);
  const y = dailyTable?.data[2];
  const x = dailyTable.columns.map(function (date, index) {
    const const_date = new Date(Date.parse(`${date[0]}-${date[1]}-${date[2]}`));
    const past = Math.round((today - const_date) / (1000 * 60 * 60 * 24));
    if(past < 14) past_14_days[past][1] = y[index];
    return const_date;
  });

  const data_sets = [{id: "Day Wise Distribution", source: y.map((y_, _) => [x[_], y_]), name: "Date"},
    {id: "Day Wise Distri. - Past 14 days", source: past_14_days, name: "Date"}]
  
  return (new ConstructEChartOption()).initSeries().lineSeries(
    "Day wise Frequency", null, true, {datasetIndex: 0}).setDataSet(data_sets)
    .setAxis(true, "time", "Date", false, {axisPointer: {value: today, snap: true, label: {backgroundColor: "#222222", color: "#fff", show: true,formatter: (params) => new Date(params.value).toDateString()}}})
    .setAxis(false, "value", "Freq.", false).setTooltip("axis").setGrid(false, {bottom: 45, left: 45}).setTitle("Day Wise Distribution", 14, "2px").raw;
}


function timelyScatter(dataset){
  const seriesMap = week_names.map(
    function (week_day) {
      return {
        name: week_day, singleAxisIndex: 0, coordinateSystem: "singleAxis", type: "scatter",
        emphasis: {focus: "series"},
        data: [],
        symbolSize: function (dataItem) {return dataItem[1] * 10;}};
  });
  const fake_date = new Date(); const am = new Date(fake_date); const pm = new Date(fake_date);
  am.setHours(0); am.setMinutes(0); pm.setHours(23); pm.setMinutes(59);
  dataset.index.forEach(function ([week_day, hr, min], index) {
    const fake = new Date(fake_date); fake.setHours(hr); fake.setMinutes(min); 
    seriesMap[week_day].data.push([fake, dataset.data[index][0]]);
  }); // though the date is fake but the time inside of it is valid
  const _options = new ConstructEChartOption().initSeries().setTooltip("item").setLegend(week_names).setTooltip("item").setGrid(true, {bottom: "10px"}).raw;
  _options.singleAxis = [{type: 'time', boundaryGap: false, height: "65%", width: "90%", splitNumber: 12,
   axisLabel: {formatter: "{HH}:{mm}", showMinLabel: true, showMaxLabel: true}, min: am, max: pm,
   name: "Update Time", nameLocation: "center", nameGap: "22"
  }]; _options.tooltip.formatter = function(value){
    return `${value.marker} ${value.seriesName}<br>${new String(value.data[0].getHours()).padStart(2, "0")}:${new String(value.data[0].getMinutes()).padStart(2, "0")} - <b>${value.data[1]}</b>`
  }; _options.series = seriesMap;
  return _options;
}

function plotForRecentlyTab(_, data, page_settings, recent_animes) {
  const no = say_no(1)[0];
  if (!data) return no;

  // VALIDATION
  if (!recent_animes) return no;

  // DATA POINTS 
  const frame = new Frame(recent_animes);

  // PLOTS
  const daily_weightage = "daily-weightage"
  const week_plot = "weekly-progress-recently-view";
  const time_went = "when-did-they-watch"

  // INIT PLOTS
  const daily_wise = createEChart(daily_weightage);
  const weekly_plot = createEChart(week_plot);
  const when_did = createEChart(time_went);

  daily_wise.setOption(
    dailyWeightage(JSON.parse(data.recently_updated_day_wise || "[]"))
  )

  weekly_plot.setOption(
    weeklyDist(JSON.parse(data.week_dist || "[]"), data.week_days || [])
  );

  when_did.setOption(
    timelyScatter(JSON.parse(data.when))
  )
  daily_wise.on("mouseover", function (line_data) {
    const date = line_data.data[0];
    if (!date) return;
    weekly_plot.dispatchAction({ type: "showTip", seriesIndex: 0, dataIndex: week_js_to_pandas(date.getDay()) });
  })

  daily_wise.on("mouseout", function () {
    weekly_plot.dispatchAction({ type: "hideTip" });
  });

  weekly_plot.on("click", { seriesIndex: 0 }, function (bar_data) {
    const markers = []; const selectedDay = week_js_to_pandas(bar_data.dataIndex, true); const selected = week_names[bar_data.dataIndex];
    const _op = daily_wise.getOption(); const current_series = _op.dataset[_op.series[0].datasetIndex];
    current_series.source.forEach((raw) => {
      if (raw[0].getDay() !== selectedDay) return;
      markers.push({coord: [raw[0], raw[1]], label: { formatter: `${raw[1]}`, color: "#fff" }})})
    daily_wise.setOption({ series: {markPoint: { data: markers }} }); const weeks = {};
    for(let week_name of week_names){weeks[week_name] = week_name === selected;} when_did.setOption({legend: {selected: weeks}});
  })

  weekly_plot.on("dblclick", { seriesIndex: 0 }, function () { // clearing the selected with the double click
    const current_series = daily_wise.getOption().series[0]; const markers = [];
    current_series["markPoint"] = { data: markers };
    daily_wise.setOption({ series: [current_series] })
    when_did.setOption({legend: {selected: week_names.map((_name) => {return {[_name]: true}})}});
  })

  const first_record = new Date(data.first_record * 1e3); const last_record = new Date(data.recent_record * 1e3);
  return [first_record.toDateString(), last_record.toDateString(), last_record.toDateString()];
}

function switchThePlots(for_called, switch_id){
  const no = say_no(1)[0]; const index = Number(for_called);
  const chart = view_e_charts_mla[switch_id.plot];
  if(!chart || dash_clientside.callback_context.triggered.length === 0 || Number.isNaN(index)) return no;
  const option = chart.getOption(); const title = option["dataset"][index].id; option.title[0].text = title; option.series[0].datasetIndex = index;
  option.legend.length && (option.legend[0].data = option.dataset[index].source.map((o) => o.name));
  chart.setOption(option); return no;
}

function searchForTheDate(raw, date){
  const records = [["id", "title", "List Status", "Total", "Completed", "Updated at", "progress"]]; const today = new Date(date); const time = today.getTime(); const date_string = today.toDateString(); const length = raw.length; let left = 0, right = length - 1; let last_found;
  while(left <= right){
    const mid = Math.ceil((left + right) / 2); const value = raw[mid];
    if(time > value[5]){ left = mid + 1; continue;}
    if(date_string === new Date(value[5]).toDateString()) last_found = mid;
    right = mid - 1;
  }
  if(Number.isNaN(last_found)) return false;
  for(value of raw.slice(last_found)){
    const stamp = new Date(value[5]); if(stamp.toDateString() !== date_string) break;
    const slice = value.slice(0, 7); slice[5] = formateTime(value[5]); records.push(slice);
  } return [records, date_string];
}

function drawThePlot(opened, askedFor, recent_animes){
  const no = say_no(1)[0]; if(!(opened && askedFor)) return no;
  const asked = "quick-update-history"; const chart = createEChart(asked);
  chart.showLoading();
  const [dataset, date_string] = searchForTheDate(JSON.parse(recent_animes), askedFor);
  if(dataset.length > 1) chart.setOption((new ConstructEChartOption().initSeries().setTitle(`Animes watched on ${date_string}`)
    .barSeries(null, "Completed", {encode: {y: "title", x: "Completed", tooltip: ["List Status", "Completed", "Total"]}, stack: "anime", emphasis: {focus: "series"}})
    .barSeries(null, "Updated", {encode: {y: "title", x: "progress", tooltip: ["Updated at"]}, stack: "anime", emphasis: {focus: "series"}})
    .setGrid(false, {left: "120px"}).setTooltip("item").setDataSet({source: dataset}).setAxis(true, "value", "Episodes", false).setAxis(false, "category", "Animes", false, {axisLabel: {width: 100, overflow: "truncate"}})).raw);
  else chart.setOption({graphic: {elements: [{type: 'text', left: 'center', top: 'center',
    style: {text: `No Animes were updated on the date: ${askedFor}`, fontSize: "1rem",
            lineDash: [0, 200], lineDashOffset: 0,
            stroke: '#696969', lineWidth: 1, fill: "coral"}
        }]}})
  chart.hideLoading();
  return no;
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  "MLAPlots": {
    plotForRecentlyTab,
    plotForOverviewTab,
    switchThePlots,
    drawThePlot
  }
});

