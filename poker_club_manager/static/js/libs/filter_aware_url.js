function buildParams(filters) {
    const params = new URLSearchParams(window.location.search);

    for (let f of filters) {
        const defaultValue = f.getAttribute("data-default") || "";
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

    const page = document.getElementById("current-page").getAttribute("value");
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