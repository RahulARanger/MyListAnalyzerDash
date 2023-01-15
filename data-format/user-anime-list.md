---
description: Format for a user Anime List
---

# User Anime List

On this page, we can understand how User's AnimeList is stored on the client side after fetching from the raw source.

### Table Format

| Column Name                         | Data Type  | Description                                                                        |
| ----------------------------------- | ---------- | ---------------------------------------------------------------------------------- |
| node.id                             | int        | ID of an Anime                                                                     |
| node.title                          | str        | Title of an Anime                                                                  |
| node.main\_picture.large            | str        | URL for an Anime's Main Picture                                                    |
| node.genres                         | list\[int] | List of id(s) pointing to Genre                                                    |
| node.start\_date                    | datetime   | start date of an Anime                                                             |
| node.mean                           | float      | Average Score of an Anime                                                          |
| node.rank                           | int        | Rank of an Anime based on the Score                                                |
| node.popularity                     | int        | Popularity Rank of an Anime                                                        |
| node.created\_at                    | datetime   | Annoucement Date of an Anime                                                       |
| node.updated\_at                    | datetime   | Date that this record was updated in the Database                                  |
| node.num\_episodes                  | int        | Number of Episodes of an Anime                                                     |
| node.media\_type                    | str        | Media type of an Anime                                                             |
| node.source                         | str        | Source of an anime                                                                 |
| node.average\_episode\_duration     | int        | Duration of an Anime in seconds                                                    |
| node.start\_season.season           | str        | Season on which, the anime was started                                             |
| node.start\_season.year             | str        | year of anime's start date                                                         |
| node.nsfw                           | str        | badges based on the nsfw                                                           |
| node.status                         | str        | Status of the Anime \[Currently Airing, Completed, Planned]                        |
| node.num\_scoring\_users            | int        | Number of Users who have provided score for anime                                  |
| node.num\_list\_users               | int        | Number of Users who have added this anime in their list                            |
| node.num\_favorites                 | int        | Number of Users who have marked this anime as their favourite.                     |
| list\_status.status                 | str        | Status set by the User on this Anime                                               |
| list\_status.score                  | int        | Score given by the User                                                            |
| list\_status.num\_episodes\_watched | int        | Number of Episodes watched for User                                                |
| list\_status.is\_rewatching         | bool       | Is the User Rewatching this anime?                                                 |
| list\_status.updated\_at            | str        | latest Timestamp of user's recent update on this anime.                            |
| list\_status.rewatch\_value         | -          | -                                                                                  |
| list\_status.priority               | -          | -                                                                                  |
| node.end\_date                      | datetime   | End date of an Anime                                                               |
| list\_status.finish\_date           | datetime   | Date on which the User has completed this anime.                                   |
| list\_status.spent                  | int        | seconds spent on this anime, \[num\_episodes\_watched \* Average Episode Duration] |

