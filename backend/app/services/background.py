"""Single-responsibility background task queue.

The ArunCore backend performs several fire-and-forget jobs (Telegram delivery,
chat history logging, debug event logging, re-ingestion triggering). All of
that work is submitted here instead of being swallowed by the request /
agent loop, so slow network calls never block chat streaming.
"""
import queue
import threading
from typing import Any, Callable


_task_queue: "queue.Queue[Any]" = queue.Queue()


def _background_worker() -> None:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    while True:
        try:
            task = _task_queue.get()
            if task is None:
                break
            func, args, kwargs = task
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"[BACKGROUND WORKER ERROR] Failed in {getattr(func, '__name__', func)}: {e}")
            finally:
                _task_queue.task_done()
        except Exception as outer_e:
            print(f"[BACKGROUND WORKER FATAL] Queue fetch failed: {outer_e}")


_thread = threading.Thread(target=_background_worker, daemon=True, name="aruncore-background")
_thread.start()


def submit_background_task(name: str, func: Callable, *args: Any, **kwargs: Any) -> bool:
    """Enqueue a callable to run on the shared background worker thread."""
    try:
        _task_queue.put((func, args, kwargs))
        print(f"[BACKGROUND] {name}: Task queued.")
        return True
    except Exception as e:
        print(f"[BACKGROUND ERROR] Failed to queue {name}: {e}")
        return False