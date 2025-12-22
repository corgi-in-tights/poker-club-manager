window.addEventListener("load", () => {
    addPageButtonListeners();

    const filters = document.getElementsByClassName("filter");
    const search = document.getElementById("event-search");
    const eventsList = document.getElementById("event-list");
    
    function buildParams() {
        const params = new URLSearchParams(window.location.search);
        for (let f of filters) {
            const defaultValue = f.getAttribute("data-default");

            if (f.value === defaultValue) {
                params.delete(f.name);
            } else {
                params.set(f.name, f.value);
            }
        }

        if (search.value) {
            params.set("q", search.value);
        } else if (params.has("q")) {
            params.delete("q");
        }
        return params;
    }

    function addPageButtonListeners() {
        const pageButtons = document.getElementsByClassName("page-button");
        for (let btn of pageButtons) {
            if (btn.hasAttribute("data-listener-attached")) continue;
            btn.setAttribute("data-listener-attached", "true");

            btn.addEventListener("click", (e) => {
                e.preventDefault();
                const newPage = parseInt(btn.getAttribute("data-page"));
                const params = buildParams();
                if (newPage <= 1) {
                    params.delete("p");
                } else {
                    params.set("p", newPage);
                }

                updateEventList(e, params);
            });
        }
    }


    function updateEventList(e, params = null) {
        const basePath = window.location.pathname;
        if (params === null) {
            params = buildParams();
        }

        // If no filters are applied, reset to the base path
        if (params.toString() === "") {
            history.pushState({}, "", basePath);
            return;
        }

        const url = `${basePath}?${params.toString()}`;
        history.pushState({}, "", url);

        fetch(url, {
            headers: { "HX-Request": "true" }
        })
            .then(r => {
                if (!r.ok) throw new Error("Network error");
                return r.text();
            })
            .then(html => {
                eventsList.innerHTML = html;
                addPageButtonListeners();
            })
            .catch(err => {
                console.error("Failed to load events:", err);
            });

    }


    for (let input of filters) {
        input.addEventListener("change", updateEventList);
    }

    // Add 'debounce' while searching, i.e. wait till user stops typing for a bit
    let searchTimer;
    search.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(applyFilters, 200);
    });

    // Back / forward support
    window.addEventListener("popstate", updateEventList);
});
