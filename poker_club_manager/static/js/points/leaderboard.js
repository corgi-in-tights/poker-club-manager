window.addEventListener("load", () => {
    createListController({
        listElementId: "leaderboard-table",
        filterSelector: "filter",
        searchInputId: "leaderboard-search",
        pageButtonSelector: "page-button",
    });
});
