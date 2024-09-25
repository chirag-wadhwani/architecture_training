import threading
import time

class LegalReentrantLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.wait_queue = []
        self.reentrant_count = 0
        self.wait_queue_lock = threading.Lock()
        self.reentrant_lock = threading.Lock()
        self.current_thread = None

    def acquire(self):
        if self.current_thread == threading.current_thread():
            with self.reentrant_lock:
                self.reentrant_count += 1
            return True
        with self.wait_queue_lock:
            self.wait_queue.append(threading.current_thread())
            while self.wait_queue[0] != threading.current_thread():
                # print(f"Lock Aquired by: {self.wait_queue[0]}")
                time.sleep(0.5)

        print(f"Lock Aquired....... {threading.current_thread()}")
        self.current_thread = threading.current_thread()
        return self.lock.acquire(blocking=True, timeout=1)

    def release(self):
        with self.reentrant_lock:
            if self.reentrant_count > 0:
                self.reentrant_count -= 1
                return True

        thread = self.wait_queue.pop(0)
        print(f"Lock release by thread: {thread}")
        self.current_thread = None
        self.lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()


lock_a = LegalReentrantLock()
threads = []

def reentrant_lock_example():
    with lock_a:
        print("Hello I am inside a")
        time.sleep(1)
        with lock_a:
            print("Trying to access the inner lock content")

for _ in range(3):
    thread = threading.Thread(target=reentrant_lock_example)
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()
