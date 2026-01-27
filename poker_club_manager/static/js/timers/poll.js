const RUNNING = 'running';
const PAUSED = 'paused';
const FINISHED = 'finished';

window.onload = (function () {
    let poller = null;
    let ticker = null;
    let lastSyncRemainingMs = null;
    let lastSyncAt = null;

    let currentState = null;
    let currentLevelId = null;
    let currentPausedAt = null;

    const stateElement = document.getElementById('timer-state');
    const levelTitleElement = document.getElementById('timer-level-title');

    const clockElement = document.getElementById('timer-clock');
    const hourElement = document.getElementById('timer-hours');
    const minuteElement = document.getElementById('timer-minutes');
    const secondElement = document.getElementById('timer-seconds');
    const setClock = (hours, minutes, seconds) => {
        hourElement.textContent = String(Math.max(0, hours)).padStart(2, '0');
        minuteElement.textContent = String(Math.max(0, minutes)).padStart(2, '0');
        secondElement.textContent = String(Math.max(0, seconds)).padStart(2, '0');
    }
    const finishClock = () => {
        clearInterval(ticker);
        ticker = null;
        clearInterval(poller);
        poller = null;
        clockElement.innerHTML = '--:--:--';
        stateElement.textContent = FINISHED;
    };

    async function pollApi() {
        try {
            const response = await fetch(pollUrl, { signal: AbortSignal.timeout(700) });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            const requiredFields = ['level', 'state', 'paused_at', 'skipped_ms'];
            for (const field of requiredFields) {
                if (!(field in data)) {
                    throw new Error(`Missing ${field} in poll response`);
                }
            }
            const { level, state, paused_at, skipped_ms } = data;

            syncServerState(level, state, paused_at, skipped_ms);

        } catch (error) {
            console.error('Error fetching timer data:', error);
        }
    }

    function validateResponse(data) {
        const requiredFields = ['level', 'state', 'paused_at', 'skipped_ms'];
        for (const field of requiredFields) {
            if (!(field in data)) {
                throw new Error(`Missing ${field} in poll response`);
            }
        }
        return { ...data };
    }

    function syncServerState(level, state, pausedAt, skippedMs) {
        // No change
        if (state !== RUNNING && state === currentState && level.id === currentLevelId) return;
        // If the state did change, controls should be re-rendered
        else if (state !== currentState) {
            document.body.dispatchEvent(new CustomEvent('timerStateChanged', {
                detail: { newState: state }
            }
            ));
        }

        // Wipe everything on finish
        if (state === FINISHED) {
            finishClock();
            return;
        }

        // Update remaining ms calculation
        let elapsedMs;

        const start = new Date(level.started_at);
        // If paused, use pausedAt time instead of 'now'
        if (state === PAUSED && pausedAt) {
            const pausedAtTime = new Date(pausedAt);
            elapsedMs = pausedAtTime - start - skippedMs;
            lastSyncAt = pausedAtTime;
            currentPausedAt = pausedAtTime;
        } else {
            const now = Date.now();
            elapsedMs = now - start - skippedMs;
            lastSyncAt = now;
            currentPausedAt = null;
        }
        lastSyncRemainingMs = Math.max(0, level.duration_seconds * 1000 - elapsedMs);

        // Update text
        let text;
        if (level.level_type == 'break') {
            text = 'Break';
        } else {
            text = 'Level ' + parseInt(level.level_index) + ': ' + level.small_blind + '/' + level.big_blind;
        }
        levelTitleElement.textContent = text;
        stateElement.textContent = state;

        currentState = state;
        currentLevelId = level.id;
    }


    function renderClock() {
        if (lastSyncRemainingMs === null) return;

        let totalSeconds;
        if (currentState === PAUSED && currentPausedAt) {
            const pausedAtTime = new Date(currentPausedAt);
            const elapsed = pausedAtTime - lastSyncAt;
            const remaining = Math.max(0, lastSyncRemainingMs - elapsed);
            totalSeconds = Math.floor(remaining / 1000);
        } else {
            const elapsed = Date.now() - lastSyncAt;
            const remaining = Math.max(0, lastSyncRemainingMs - elapsed);
            totalSeconds = Math.floor(remaining / 1000);
        }

        setClock(
            Math.floor(totalSeconds / 3600),
            Math.floor((totalSeconds % 3600) / 60),
            totalSeconds % 60
        );
    }


    // Poll the server to check for state updates
    poller = setInterval(pollApi, 900);
    // Keep locally updating the clock every 50ms
    ticker = setInterval(renderClock, 200);
    pollApi();

    // Anytime htmx updates the timer controls, re-poll the server
    document.addEventListener('htmx:afterOnLoad', (event) => {
        if (event.detail.target.id === 'timer-controls') {
            pollApi();
        }
    });
});
