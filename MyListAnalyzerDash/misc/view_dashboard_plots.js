const week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const view_e_charts_mla = {}; // be a good boy
const status_colors = {"Completed": "#90EE90", "Watching": "#87CEEB", "Dropped": "#FFCCCB", "Hold": "#FCE883"}

// // HELPER FUNCTIONS

// UPDATING THEME
fetch('/MLA/assets/theme.json')
  .then(r => r.json())
  .then(theme => {
    echarts.registerTheme('essos', theme);
  });

// FOR RESIZING ALL PLOTS FOR THE VIEW DASHBOARD _if present_
window.addEventListener('resize', function () {
  Object.values(view_e_charts_mla).forEach((plot) => plot?.resize());
});


// USE this if and only if you need to use whole row or column or TABLE
// not for particular cell
class Frame {
  raw;
  constructor(raw) {
    this.raw = JSON.parse(raw);
  }

  col(col_index) {
    return this.raw.map((row) => row[col_index]);
  }

  row(row_index) {
    return this.raw[row_index]
  }

  rows(...indices){
    return this.raw.map((row) => indices.map((index) => row[index]))
  }
}


// for creating Echart
function createEChart(element, on) {
  const chart = echarts.init(element, "essos", { renderer: on || 'svg' });
  new ResizeObserver(() => chart.resize()).observe(element);
  return chart
}

// for displaying plots
function displayPlots(...plots) {
  plots.forEach((plot) => view_e_charts_mla[plot]?.dispose());
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

  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    title: { text: "Range of Anime Episodes", left: "center", textStyle: { fontSize: 16 } },
    xAxis: { type: "category", data: keys, splitLine: { show: false }, name: "Episode Range" },
    yAxis: { type: "value", splitLine: { show: false }, name: "Anime Count" },
    visualMap: {
      orient: "horizontal", left: "center", min: Math.min(...values), max: Math.max(...values),
      text: ["Mostly Seen", "Least ones"],
      dimension: 1,
    },
    series: [{
      data: values,
      type: "bar"
    }],
    toolbox: generalToolBox()
  };

}


function plotRatingsDist(data) {
  const ratings = Object.keys(data);

  return {
    title: { text: "Age Rating over Animes", top: "90%", left: "center", textStyle: { fontSize: 16 } },
    legend: { orient: 'horizontal', x: 'left', data: ratings, type: "scroll" },
    tooltip: { trigger: "item", formatter: "{a} ({c} | {d}%)<br/>{b}" },
    series: [
      {
        type: 'pie',
        radius: '65%',
        name: "Rating",
        center: ['50%', '50%'],
        selectedMode: 'multiple',
        data: ratings.map(function (label) { return { value: data[label], name: label }; })
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
    toolbox: { show: true, feature: { saveAsImage: { show: true } } }
  };
}


function plotForOverviewTab(_, data, page_settings) {
  const no = say_no(1)[0];
  if (!data) return no;

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


  return option = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    title: { text: "Weekly Frequency", left: "center", textStyle: { fontSize: 14 } },
    grid: { top: 54, containLabel: true, left: 10, height: "70%" },
    xAxis: [
      {
        type: "category",
        data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        axisPointer: {
          type: "shadow"
        },
        axisTick: {
          alignWithLabel: true
        },
        splitLine: {
          show: false
        }
      }
    ],
    yAxis: [
      {
        splitLine: {
          show: false
        },
        type: "value",
        name: "No. of Eps.",
        axisLabel: {
          formatter: "{value} eps"
        }
      },
      {
        splitLine: {
          show: false
        },
        type: "value",
        name: "Eps / Per wk",
        axisLabel: {
          formatter: "{value} / wk"
        }
      }
    ],
    series: [
      {
        type: "bar",
        name: "Number of Episodes",
        data: eps_watched_per_week,
        itemStyle,
        emphasis: onHover
      },
      { name: "Average", data: avg_s, type: "line", yAxisIndex: 1 }
    ],
    aria: { enabled: true },
    toolbox: generalToolBox()
  };
}


function dailyWeightage(dailyTable) {
  const x = dailyTable.columns.map(function (date) {
    return new Date(Date.parse(`${date[0]}-${date[1]}-${date[2]}`));
  });
  const y = dailyTable?.data[2];

  return {
    title: {text: "Day Wise Distribution", left: "center", textStyle: { fontSize: 14 }},
    tooltip: {trigger: "axis"},
    xAxis: {splitLine: {show: false},
      type: "time",
      nameLocation: "middle"
    },
    yAxis: {
      type: 'value', splitLine: {
        show: false
      },
    },
    series: [
      {
        data: y.map((y_, _) => { return [x[_], y_] }),
        type: 'line',
        smooth: true
      }
    ]
  };

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
  displayPlots(daily_weightage, week_plot, bar_race);

  // INIT PLOTS
  const daily_wise = createEChart(document.getElementById(daily_weightage));
  const weekly_plot = createEChart(document.getElementById(week_plot));
  const bar_race_plot = createEChart(document.getElementById(bar_race));


  daily_wise.setOption(
    dailyWeightage(JSON.parse(data.recently_updated_day_wise || "[]"))
  )

  weekly_plot.setOption(
    weeklyDist(JSON.parse(data.week_dist || "[]"), data.week_days || [])
  );

  bar_race_plot.setOption(quickHistory(frame.rows(0, 1, 2, 3, 4, 5))); // Id, Anime Name, Status, up_until, total

  // SAVING PLOTS
  view_e_charts_mla[week_plot] = weekly_plot;
  view_e_charts_mla[daily_weightage] = daily_wise
  view_e_charts_mla[bar_race] = bar_race_plot;


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
  
  if(index)
      raw_option.series[series_index].data = [raw[index], ...series_data.filter((row) => row[0] !== raw[index][0])]
  else
     raw_option.series[series_index].data = [];
  
  index && (raw_option.graphic[0].elements[0].style.text = new Date(raw[index][5]).toLocaleString());
  bar_race_plot.setOption(raw_option);
  setTimeout(() => template(index + 1), 1e3);
}

template(0);
  return no;
}




window.dash_clientside = Object.assign({}, window.dash_clientside, {
  "MLAPlots": {
    plotForRecentlyTab,
    plotForOverviewTab
  }
});

