# Contributing to the project

## Starting the project
1. Clone the repository
2. Make sure `just`, `ruff`, `docker` are installed
3. Build the docker images using `just build`
4. Start everything using `just up`
5. Attach logs `just logs`, make sure it says "server is up at ", might take a minute
6. Then, in a seperate or the current terminal window, run `just migrate` to create the DB tables and everything
7. `just seed` to initialize all the sample data
8. Create a superuser using `just manage createsuperuser`
9. Should be running at https://localhost:8000

I would recommend working without autosave, or the refresh can be funky (refreshes every edit), though for templating its not a big deal. Sometimes cache can be a bitch for static files, work in incognito, that way you can close the window to clear the cache.

## Templates
Read:
- docs/template-syntax.md
- docs/views-template.md

Should cover everything for frontend.
