---
description: Pre-Dashboard Process
---

# 🏗 Processes

From this page, you can understand how the pre-dashboard setup was performed.

Below are the Steps followed for setting up the Dashboard:

1. Validating the User name entered, if "For You" then we will fetch your name, else we will directly proceed with the next step
2. Fetching the User's Anime List, in this step, if the User has more than 1k Animes in his / her list we usually send consecutive requests to fetch the User's Anime List, but do **note that we can only fetch a maximum of 5k Animes updated Recently.**
3. And then we fetch User's Recent AnimeList and store it in a [particular format](https://app.gitbook.com/s/VANLa1yks9zEvIdYipea/\~/changes/xTQj8lMRW0oM7AUi1lj5/data-format/recent-anime-list).
4. Now we have the required data source, we now will save it in the Client's Browser Memory. `dcc.Store.`

Data Sources

1. [User Anime List](../data-format/user-anime-list.md)
2. [Recent Anime List](https://app.gitbook.com/s/VANLa1yks9zEvIdYipea/\~/changes/xTQj8lMRW0oM7AUi1lj5/data-format/recent-anime-list)
