function copyUrl(btn) {
    const absoluteUrl = window.location.origin + btn.dataset.url;
    navigator.clipboard.writeText(absoluteUrl);
    btn.innerText = "URL Copied!";
    setTimeout(() => {
        btn.innerText = "Copy URL";
    }, 2000);
}


function sendRSVP(btn) {
    const url = btn.getAttribute('data-rsvp-url');

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            "status": "going"
        })
    })
        .then(response => {
            if (response.ok) {
                btn.replaceWith('RSVP successful!');
            } else {
                alert('Failed to RSVP. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
}



function addRSVPButtonListeners() {
    const rsvpButtons = document.getElementsByClassName("rsvp-button");

    for (let btn of rsvpButtons) {
        if (btn.hasAttribute("data-listener-attached")) continue;
        btn.setAttribute("data-listener-attached", "true");

        btn.addEventListener("click", (e) => {
            e.preventDefault();
            sendRSVP(e.target);
        });
    }
}


window.addEventListener("load", () => {
    createListController({
        listElementId: "event-list",
        filterSelector: "filter",
        searchInputId: "event-search",
        pageButtonSelector: "page-button",
        attachListeners: addRSVPButtonListeners,
    });
});
