import os
import multiprocessing
import signal
import sys
import threading
from functools import wraps
import random
from time import sleep


class PublisherManager(object):
    def __init__(self):
        self.manager_dict = multiprocessing.Manager().dict()

    def publish(self, val):
        self.manager_dict['manager_key'] = val

class SigTermException(Exception):
    pass


def sigtermhandler(signum, frame):
    raise SigTermException('sigterm')

def worker(manager_dict, my_object):
    try:
        while True:
            my_object.attr_1 = manager_dict.manager_dict.get('manager_key')
            print("got item {} in process {}".format(my_object.attr_1, os.getpid()))
            sleep(5)
    except SigTermException:
        print("Received SIGTERM")

def _process_publish_things(master_queue):
    try:
        while True:
            rand_number = random.randint(0, 500)
            master_queue.publish(rand_number)
            print(f"PUBLISHED {rand_number}")
            sleep(2)
    except SigTermException:
        print("Received SIGTERM")

signal.signal(signal.SIGTERM, sigtermhandler)

def publish_things(master_publisher):
    try:
        # p = multiprocessing.Process(target=_process_publish_things, args=(master_queue,))
        p = threading.Thread(target=_process_publish_things, args=(master_publisher,))
        p.start()
    except SigTermException:
        p.join()
        print("Received SIGTERM")

class MyClass():
    attr_1 = ""
    attr_2 = ""

my_object = MyClass()

master_publisher = PublisherManager()
#publish_things(master_publisher)



def start_listener():
    try:
        global master_publisher
        thr = threading.Thread(target=worker, args=(master_publisher, my_object,))
        thr.start()
    except SigTermException:
        thr.join()
        print("Received SIGTERM")

if __name__ == "__main__":
    publish_things(master_publisher)
    my_object = MyClass()
    thr = threading.Thread(target=worker, args=(master_publisher, my_object,))
    thr.start()
    # for _ in range(3):
    #
    #     p = Process(target=worker, args=(q.register(),))
    #     p.start()
    #     processes.append(p)
    # q.publish('1')
    # q.publish(2)
    # q.publish(None)  # Shut down workers
    #
    # for p in processes:
    #     p.join()
    for i in range(400):
        sleep(5)
        print(f"my_object vale {my_object.attr_1}")
    thr.join()