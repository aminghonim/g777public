from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging
from typing import Callable, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeChangeHandler(FileSystemEventHandler):
    """
    Handles file system events for code changes.
    """

    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"File modified: {event.src_path}")
            if self.callback:
                self.callback(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"File created: {event.src_path}")
            if self.callback:
                self.callback(event.src_path, "created")

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")
            if self.callback:
                self.callback(event.src_path, "deleted")


class FileWatcher:
    """
    Monitors a directory for file changes using watchdog.
    """

    def __init__(self, path: str, callback: Optional[Callable] = None):
        self.path = path
        self.callback = callback
        self.observer = Observer()
        self.event_handler = CodeChangeHandler(callback)

    def start(self):
        """Starts the file watcher."""
        logger.info(f"Starting FileWatcher on: {self.path}")
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()

    def stop(self):
        """Stops the file watcher."""
        logger.info("Stopping FileWatcher...")
        self.observer.stop()
        self.observer.join()


if __name__ == "__main__":
    # Test execution
    def test_callback(file_path, event_type):
        print(f"[TEST CALLBACK] {event_type.upper()}: {file_path}")

    watcher = FileWatcher(".", callback=test_callback)
    try:
        watcher.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
