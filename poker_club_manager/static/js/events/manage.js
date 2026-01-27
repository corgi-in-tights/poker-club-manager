window.onload = function () {
    addDeleteButtonListeners();

    const addParticipantUrl = document.getElementById("add-participant-url").value;
    const searchInput = document.getElementById("search-input");
    const dataURL = searchInput.getAttribute("data-url");

    function update() {
        const value = searchInput.value.trim();
        if (value === "") {
            document.getElementById("participant-search-results").innerHTML = "";
            return;
        }

        fetch(dataURL + "?" + new URLSearchParams({
            query: value
        })).then(
            response => response.json()
        ).then(
            data => {
                const resultsContainer = document.getElementById("participant-search-results");
                resultsContainer.innerHTML = "";

                data.results.forEach(user => {
                    const div = document.createElement("div");
                    div.classList.add("search-result-item");
                    div.innerHTML = `
                    <button class="add-participant-button"
                            hx-post="${addParticipantUrl}"
                            hx-vals='{"user_id": "${user.id}"}'
                            hx-target="#participant-list"
                            hx-swap="innerHTML">
                        <span class="search-result-name">${user.name}</span>
                    </button>
                    `;
                    resultsContainer.appendChild(div);
                });
            }
        )
    }

    if (searchInput !== undefined && dataURL !== undefined) {
        let timer;
        searchInput.addEventListener("input", () => {
            clearTimeout(timer);
            timer = setTimeout(update, 200);
        });
    }
};
