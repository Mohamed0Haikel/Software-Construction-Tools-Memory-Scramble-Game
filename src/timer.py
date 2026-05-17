"""
Countdown timer running in a dedicated thread.

Concurrency concepts (from the lecture):
  • **Shared Memory** — `time_remaining` is shared between the timer
    thread and the main thread.  A `threading.Lock` prevents race
    conditions caused by interleaving of read/write operations.
  • **Message Passing** — The timer communicates events to the GUI
    via a `queue.Queue` (TICK / TIMEOUT messages).  This decouples
    the producer (timer thread) from the consumer (GUI thread) and
    avoids direct cross-thread GUI calls.
  • **Daemon Thread** — The timer thread is marked as daemon so it
    is automatically terminated when the main process exits.
"""

import threading
import queue
import time


class CountdownTimer:
    """A countdown timer that ticks every second in its own thread."""

    
    MSG_TICK = "TICK"        
    MSG_TIMEOUT = "TIMEOUT"  

    def __init__(
        self,
        duration_seconds: int,
        message_queue: queue.Queue,
    ) -> None:
        self._duration = duration_seconds
        self._time_remaining = duration_seconds

       
        self._lock = threading.Lock()

        
        self._message_queue = message_queue

        self._running = False
        self._thread: threading.Thread | None = None


    @property
    def time_remaining(self) -> int:
        """Thread-safe read of the shared `time_remaining` variable.
        """
        with self._lock:
            return self._time_remaining


    def start(self) -> None:
        """Spawn the timer thread and begin counting down."""
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,   
            name="CountdownTimer",
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the timer thread to stop and wait for it to finish."""
        self._running = False
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2)


    def _run(self) -> None:
        """Main loop executed inside the timer thread.
        """
        while self._running:
            time.sleep(1)

            with self._lock:
                self._time_remaining -= 1
                remaining = self._time_remaining

            if remaining > 0:
                self._message_queue.put((self.MSG_TICK, remaining))
            else:
                self._message_queue.put((self.MSG_TIMEOUT, 0))
                self._running = False