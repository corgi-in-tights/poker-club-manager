# Views & Templates

### root (config/urls.py)
Path                        | Reverse URL Name         | Template/Description          
--------------------------- | ------------------------ | -----------------------------
/                           | home                     | pages/home.html
/about                      | about                    | pages/about.html

### events (events/urls.py)
All except list get `event` as the current target event.
list gets `events, page, max_page, filters, default_filters`.
See `events/models.py#Event` for reference.

Path                        | Reverse URL Name         | Template/Description          
--------------------------- | ------------------------ | -----------------------------
/events/                    | events:list              | events/list.html (list events)
/events/check-in            | events:check_into_first_active | (check into first active event)
/events/<event_id>/         | events:detail            | events/detail.html (event detail view)
/events/<event_id>/check-in | events:check_in          | events/check_in.html (check in to event)
/events/create/             | events:create            | events/create.html (create event)
/events/<event_id>/manage/  | events:manage            | events/manage.html (manage event)
/events/_rsvp_button/<event_id> | events:rsvp_button    | events/partials/rsvp_button.html


### points (points/urls.py)
Leaderboard gets `members`, and `season` which is the current active season.
Archive gets `seasons`.
See `common/models.py#SeasonMembership`, `common/models.py#Season`

Path                              | Reverse URL Name         | Template/Description
---------------------------------- | ------------------------ | -----------------------------
/points/                          | points:leaderboard       | points/leaderboard.html (current leaderboard)
/points/archive/                  | points:archive           | points/archive.html (archive overview)
/points/archive/<season_id>/       | points:archived-leaderboard | points/leaderboard.html (archived leaderboard for season)
any leaderboard url       |  | points/out_of_season.html (when no active season can be found)

### timers (timers/urls.py)
Timers get `timer`, see `timers/models.py#BlindsTimer` for reference.
Path                              | Reverse URL Name         | Template/Description
---------------------------------- | ------------------------ | -----------------------------
/timers/                          | timers:active            | timers/active.html (active timers)
/timers/create/                   | timers:create            | timers/create.html (create timer)
/timers/<timer_id>/               | timers:detail            | timers/detail.html (timer detail)
/timers/_control/<timer_id>/      | timers:control           | timers/partials/control.html (timer control partial)