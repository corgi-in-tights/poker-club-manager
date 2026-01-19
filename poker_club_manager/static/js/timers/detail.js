window.onload = function () {
    const streamUrl = document.getElementById("timer-stream-url").value;
    const eventSource = new EventSource(streamUrl);

    eventSource.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log("Got data:", data);
        document.getElementById("level").innerText = data.current_level_index;
        document.getElementById("level_started_at").innerText = data.level_started_at;
        document.getElementById("paused").innerText = data.is_paused;

        if (data.is_finished) {
            eventSource.close();
        }
    };
}
