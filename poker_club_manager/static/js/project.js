function getCSRFToken() {
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.content : null;
};

function postJSON(url, data = {}) {
    return fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(data),
    });
}
