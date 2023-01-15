---
description: Info related to the Hosted Site
---

# 📰 Website

You can always visit My-List-Analyzer's [Home page](https://rahularanger.vercel.app/MLA). As of now we only have a single Dashboard - The User View Dashboard. which can be seen [here](https://rahularanger.vercel.app/MLA/view/).

## Host

Thanks, [Vercel](https://vercel.com/) for hosting My-List-Analyzer :heart:

Please refer to the Root Project Repository for more information. To conclude, The Project was hosted under the [Vercel - Hobby Plan](https://vercel.com/docs/concepts/limits/overview)

## Architecture

We are following [Three - Tier Architecture](https://www.ibm.com/in-en/cloud/learn/three-tier-architecture) same as the parent repo.

### Presentation Tier

For this level, we have scripts present [here](https://github.com/RahulARanger/MyListAnalyzerDash) (in JS, CSS, and Python).

[Dash ](https://dash.plotly.com/introduction)Application renders layout using [React ](https://reactjs.org/)Library. Most of the beautiful and interactive components seen were provided by [Mantine ](https://mantine.dev/)through [Dash-Mantine](https://www.dash-mantine-components.com/) and [Swiper](https://swiperjs.com/).

For presenting various plots, we use [Plotly ](https://plotly.com/python/)and [Apache ECharts](https://echarts.apache.org/en/images/logo.png).&#x20;

### Application Tier

At this Tier, we have python scripts written in [MyListAnalyzerAPI](https://github.com/RahulARanger/MyListAnalyzerAPI).&#x20;

MyListAnalyzerAPI fetches the required data source from MyAnimeList and returns them in a format that is later processed to return the required results. Various insights and results were also calculated by MyListAnalyzerAPI.

### Data Tier

Thanks to Public API provided by MyAnimeList&#x20;
