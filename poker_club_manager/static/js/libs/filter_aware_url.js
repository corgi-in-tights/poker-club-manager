function buildParams(filters) {
    const params = new URLSearchParams(window.location.search);

    for (let f of filters) {
        const defaultValue = f.getAttribute("data-default") || "";
        if (f.type === "checkbox") {
            const val = f.checked ? "1" : "0";
            if (val === defaultValue)
                params.delete(f.name);
            else params.set(f.name, val);
            continue;
        } 
        
        if (f.value === defaultValue) {
            params.delete(f.name);
        } else {
            params.set(f.name, f.value);
        }
    }

    return params;
}

function updateHistory() {
    const filters = document.getElementsByClassName("filter");
    const params = buildParams(filters);

    const pageEl = document.getElementById("current-page");
    const page = pageEl ? pageEl.value : null;
    if (page && page !== "1") {
        params.set("p", page);
    } else {
        params.delete("p");
    }

    const basePath = window.location.pathname;
    const url =
        params.toString() === ""
            ? basePath
            : `${basePath}?${params.toString()}`;

    history.pushState({}, "", url);
}

window.onload = function () {
    updateHistory();
};
