function createListController({
    listElementId,
    filterSelector,
    searchInputId,
    pageButtonSelector,
    attachListeners = () => {},
    partialHeader = "HX-Request",
}) {
    const listEl = document.getElementById(listElementId);
    const filters = document.getElementsByClassName(filterSelector);
    const search = searchInputId
        ? document.getElementById(searchInputId)
        : null;

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

        if (search) {
            if (search.value) params.set("q", search.value);
            else params.delete("q");
        }

        return params;
    }

    function update(params = null) {
        const basePath = window.location.pathname;
        if (!params) params = buildParams();

        const url =
            params.toString() === ""
                ? basePath
                : `${basePath}?${params.toString()}`;

        history.pushState({}, "", url);

        fetch(url, {
            headers: { [partialHeader]: "true" },
        })
            .then(r => r.text())
            .then(html => {
                listEl.innerHTML = html;
                attachPageButtons();
                attachListeners();
            });
    }

    function attachPageButtons() {
        const buttons = document.getElementsByClassName(pageButtonSelector);
        for (let btn of buttons) {
            if (btn.dataset.listenerAttached) continue;
            btn.dataset.listenerAttached = "true";

            btn.addEventListener("click", e => {
                e.preventDefault();
                const params = buildParams();
                const page = btn.dataset.page;
                if (page <= 1) params.delete("p");
                else params.set("p", page);
                update(params);
            });
        }
    }

    for (let f of filters) {
        f.addEventListener("change", () => update());
    }

    if (search) {
        let timer;
        search.addEventListener("input", () => {
            clearTimeout(timer);
            timer = setTimeout(update, 200);
        });
    }

    window.addEventListener("popstate", () => update());

    attachPageButtons();
    attachListeners();
}
