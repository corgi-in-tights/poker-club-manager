function removeParticipant(url, onResponse) {
    fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
    .then(response => onResponse(response))
}

function addParticipant(baseUrl, userId, onSuccess) {
    fetch(baseUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ user_id: userId }),
    })
    .then(response => {
        if (response.ok) {
            onSuccess(response);
        } else {
            throw new Error('Failed to add participant.');
        }
    });
}


function addDeleteButtonListeners() {
    const deleteButtons = document.querySelectorAll('.delete-button');

    deleteButtons.forEach((button) => {
        if (button.getAttribute('data-listener-added')) return;
        button.setAttribute('data-listener-added', 'true');

        button.addEventListener('click', (e) => {
            e.preventDefault();
            const url = button.getAttribute('data-url');
            if (confirm('Are you sure you want to delete this item?')) {
                removeParticipant(url, (response) => {
                    if (response.ok) {
                        button.closest('tr').remove();
                    } else {
                        alert('Failed to delete the item.');
                    }
                });
            }
        });
    });
}

window.onload = function() {
    addDeleteButtonListeners();
    
    const searchInput = document.getElementById("search-input");
    const dataURL = searchInput ? searchInput.getAttribute("data-url") : null;

    function update() {
        const value = searchInput.value.trim();
        if (value === "") {
            document.getElementById("search-results").innerHTML = "";
            return;
        }

        fetch(dataURL + "?" + new URLSearchParams({
            query: value
        })).then(
            response => response.json()
        ).then(
            data => {
                const resultsContainer = document.getElementById("search-results");
                resultsContainer.innerHTML = "";
                
                data.results.forEach(user => {
                    const btn = document.createElement("btn");
                    btn.innerHTML = `
                        <span>${user.username}</span>
                        <span>${user.name}</span>
                    `;
                    resultsContainer.appendChild(btn);
                });

                addDeleteButtonListeners();
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

    const addParticipantForm = document.getElementById("add-participant-form");
    const addParticipantBaseUrl = addParticipantForm.getAttribute("data-url");

    addParticipantForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const participantIdentifier = addParticipantForm.elements["participant_identifier"].value.trim();
        if (participantIdentifier === "") {
            alert("Please enter a valid identifier.");
            return;
        }

        addParticipant(addParticipantBaseUrl, participantIdentifier, () => {
            addParticipantForm.elements["participant_identifier"].value = "";
            update();
        });
    });

    
};