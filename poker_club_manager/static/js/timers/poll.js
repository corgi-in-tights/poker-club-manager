const RUNNING = 'running';
const PAUSED = 'paused';
const FINISHED = 'finished';

window.onload = (function () {
    let currentState = null;
    let currentLevelId = null;
    let clientPausedAt = null;

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

    let ticker = null;
    const startClockTicker = () => {
        if (ticker === null) {
            ticker = setInterval(() => {
                let hours = parseInt(hourElement.textContent);
                let minutes = parseInt(minuteElement.textContent);
                let seconds = parseInt(secondElement.textContent);

                if (seconds > 0) {
                    seconds -= 1;
                } else {
                    if (minutes > 0) {
                        minutes -= 1;
                        seconds = 59;
                    } else {
                        if (hours > 0) {
                            hours -= 1;
                            minutes = 59;
                            seconds = 59;
                        } else {
                            // Timer has reached zero
                            stopClockTicker();
                            return;
                        }
                    }
                }
                setClock(hours, minutes, seconds);
            }, 1000);
        }
    };
    const stopClockTicker = () => {
        if (ticker !== null) {
            clearInterval(ticker);
            ticker = null;
        }
    };
    const clearClock = () => {
        clockElement.innerHTML = '--:--:--';
    };

    async function pollApi() {
        try {
            const response = await fetch(pollUrl);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const { level, state, skipped_ms, paused_at } = validateResponse(await response.json());
            attemptToSyncWithServer(level, state, paused_at, skipped_ms);

        } catch (error) {
            console.error('Error fetching timer data:', error);
        }
    }

    function validateResponse(data) {
        const requiredFields = ['level', 'state', 'skipped_ms'];
        for (const field of requiredFields) {
            if (!(field in data)) {
                throw new Error(`Missing ${field} in poll response`);
            }
        }
        return { ...data };
    }

    function attemptToSyncWithServer(level, state, timerPausedAt, skippedMs) {
        if (state !== PAUSED) timerPausedAt = null; // ignore paused_at if not paused, because desync

        const remainingServerMs = calculateRemainingMs(level.started_at, level.duration_seconds, timerPausedAt, skippedMs);
        if (!isClientOutOfSync(remainingServerMs, level, state)) return;

        console.log("Client out of sync, updating timer display from server data.");

        updateTimerState(level, state);
        updateTimerDisplay(remainingServerMs, level, state);
    }

    function isClientOutOfSync(remainingServerMs, level, state) {
        // Either level or state changed definitely 
        // or out of sync if more than 2 seconds difference
        if (currentLevelId !== level.id || currentState !== state)
            return true;

        try {
            const displayedTotalSeconds = parseInt(hourElement.textContent) * 3600 +
                parseInt(minuteElement.textContent) * 60 +
                parseInt(secondElement.textContent);
            const serverTotalSeconds = Math.ceil(remainingServerMs / 1000);

            return Math.abs(displayedTotalSeconds - serverTotalSeconds) > 2;
        } catch (e) {
            return true; // if parsing fails, consider out of sync
        }
    }

    function calculateRemainingMs(levelStart, levelDurationSeconds, timerPausedAt, skippedMs = 0) {
        const start = new Date(levelStart);
        // essentially if the server paused the timer, use that time as the paused point
        // because 'now' is not advancing while paused
        let elapsed;
        if (timerPausedAt !== null && timerPausedAt !== undefined) {
            elapsed = new Date(timerPausedAt) - start - skippedMs;
        } else {
            const now = new Date();
            elapsed = now - start - skippedMs;
        }
        const remainderMs = Math.max(0, Math.floor(levelDurationSeconds * 1000 - elapsed));
        return remainderMs;
    }

    function updateTimerState(level, state) {
        if (state === FINISHED) {
            stopClockTicker();
            clearClock();
        } else if (state === RUNNING) {
            // restart ticker at the start of the next second
            if (currentState !== RUNNING) {
                stopClockTicker();
                const now = new Date();
                const delay = 1000 - (now.getMilliseconds());
                setTimeout(() => {
                    startClockTicker();
                }, delay);
            }
        } else if (state === PAUSED) {
            stopClockTicker();
        }

        currentLevelId = level.id;
        currentState = state;
    }

    function updateTimerDisplay(remainingServerMs, level, state) {
        const updateClock = () => {
            const totalSeconds = Math.floor(remainingServerMs / 1000);
            const hours = Math.floor(totalSeconds / 3600);
            const minutes = Math.floor((totalSeconds % 3600) / 60);
            const seconds = totalSeconds % 60;
            setClock(hours, minutes, seconds);
        }

        const updateText = () => {
            let text;
            if (level.level_type == 'break') {
                text = 'Break';
            } else {
                text = 'Level ' + parseInt(level.level_index) + ': ' + level.small_blind + '/' + level.big_blind;
            }
            levelTitleElement.textContent = text;

            stateElement.textContent = state;
        }

        updateClock();
        updateText();
    }


    pollApi();
    setInterval(pollApi, 900);

    document.addEventListener('htmx:afterOnLoad', (event) => {
        if (event.detail.target.id === 'timer-controls') {
            pollApi();
        }
    });
});