import json
import time
import threading
from datetime import datetime
from filelock import FileLock
import logging

LOCK_FILE = 'scheduler.lock'
DATA_FILE = 'scheduler.json'
LOG_FILE = 'scheduler.log'

FUNC_MAP = {}

lock = threading.Lock()

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def task(func):
    FUNC_MAP[func.__name__] = func
    return func

@task
def hello():
    with lock:
        logging.info("Hello!")

@task
def bye():
    with lock:
        logging.info("Bye!!!")

def consumer():
    while True:
        with FileLock(LOCK_FILE):
            try:
                with open(DATA_FILE, 'r') as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []

        current_time = datetime.now().isoformat()
        for task_data in data:
            if task_data["time"] <= current_time:
                t = threading.Thread(target=FUNC_MAP[task_data["function"]])
                t.start()
                data.remove(task_data)

                with FileLock(LOCK_FILE):
                    with open(DATA_FILE, 'w') as file:
                        json.dump(data, file)
            else:
                break

        time.sleep(1)

def get_user_input():
    func_name = input("Enter the function name (hello/bye): ")
    execution_time = input("Enter the execution time (YYYY-MM-DD HH:MM:SS): ")

    try:
        execution_time = datetime.strptime(execution_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        with lock:
            logging.warning("Invalid time format provided.")
        return None, None

    return func_name, execution_time

def insert_in_order(data, task):
    for i, entry in enumerate(data):
        if task["time"] < entry["time"]:
            data.insert(i, task)
            return
    data.append(task)

def producer():
    while True:
        func_name, execution_time = get_user_input()
        if not (func_name and execution_time):
            continue

        task = {"function": func_name, "time": execution_time.isoformat()}

        with FileLock(LOCK_FILE):
            try:
                with open(DATA_FILE, 'r') as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []

            insert_in_order(data, task)

            with open(DATA_FILE, 'w') as file:
                json.dump(data, file)

if __name__ == "__main__":
    threading.Thread(target=consumer).start()  # Start consumer in a separate thread
    producer()