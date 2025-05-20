import threading
import time

class Timer:
    def __init__(self, interval_sec, callback):
        self.interval = interval_sec
        self.callback = callback
        self._running = False
    
    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True  # Daemon thread exits when main program exits
        self._thread.start()
    
    def stop(self):
        self._running = False
        if hasattr(self, '_thread'):
            self._thread.join()  # Wait for thread to finish
    
    def is_running(self):
        return self._running
    
    def _run(self):
        while self._running:
            start_time = time.time()
            should_stop = self.callback()  # Callback returns True to stop
            if should_stop:
                self._running = False
                break
            elapsed = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)
