---
description: Format for a user Anime List
---

# User Anime List

#### Data Source: [API Endpoint](https://myanimelist.net/apiconfig/references/api/v2#operation/users\_user\_id\_animelist\_get)

#### Columns with their data types

```markup
node.id                               int64
node.title                           object
node.main_picture.large              object
node.genres                          object
node.start_date                      object
node.end_date                        object
node.mean                           float64
node.rank                           float64
node.popularity                       int64
node.created_at                      object
node.updated_at                      object
node.num_episodes                     int64
node.media_type                      object
node.source                          object
node.average_episode_duration         int64
node.rating                          object
node.studios                         object
node.start_season.year              float64
node.start_season.season             object
node.nsfw                            object
node.status                          object
node.num_scoring_users                int64
node.num_list_users                   int64
node.num_favorites                    int64
list_status.status                   object
list_status.score                     int64
list_status.num_episodes_watched      int64
list_status.is_rewatching              bool
list_status.updated_at               object
list_status.start_date               object
list_status.num_times_rewatched       int64
list_status.rewatch_value             int64
list_status.priority                  int64
list_status.finish_date              object
list_status.spent                   float64
dtype: object
```
