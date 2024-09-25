import threading
import time
lock1 = threading.Lock()
lock2 = threading.Lock()

def thread1_routine():
    with lock1:
        print("T1: lock1 acquired")
        time.sleep(1)
    with lock2:
        print("T1: lock2 acquired")

def thread2_routine():
    with lock2:
        print("T2: lock2 acquired")
        time.sleep(1)
    with lock1:
        print("T2: lock1 acquired")
        
t1 = threading.Thread(target=thread1_routine)
t2 = threading.Thread(target=thread2_routine)

t1.start()
t2.start()

# Join the threads
t1.join()
t2.join()

print("Done")