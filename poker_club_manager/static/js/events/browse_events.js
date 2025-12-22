window.addEventListener("load", () => {
    const filters = document.getElementsByClassName("filter");
    const eventsList = document.getElementById("event-list");
    const search = document.getElementById("event-search");

    function buildParams() {
        const params = new URLSearchParams(window.location.search);
        for (let f of filters) {
            const defaultValue = f.getAttribute("data-default");
            if (f.value && f.value !== defaultValue) {
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

    function applyFilters() {
        const url = `/events?${buildParams().toString()}`;
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
            })
            .catch(err => {
                console.error("Failed to load events:", err);
            });
    }

    for (let input of filters) {
        input.addEventListener("change", applyFilters);
    }

    // Add 'debounce' while searching, i.e. wait till user stops typing for a bit
    let searchTimer;
    search.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(applyFilters, 200);
    });

    // Back / forward support
    window.addEventListener("popstate", applyFilters);
});
