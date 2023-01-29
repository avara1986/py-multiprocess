import queue
import os
import multiprocessing
import threading
import weakref
from functools import wraps
import random
from time import sleep

import typing
import wrapt

_T = typing.TypeVar("_T")
_resetable_objects = weakref.WeakSet()  # type: weakref.WeakSet[ResetObject]

class ResetObject(wrapt.ObjectProxy, typing.Generic[_T]):
    """An object wrapper object that is fork-safe and resets itself after a fork.
    When a Python process forks, a Lock can be in any state, locked or not, by any thread. Since after fork all threads
    are gone, Lock objects needs to be reset. CPython does this with an internal `threading._after_fork` function. We
    use the same mechanism here.
    """

    def __init__(
        self, wrapped_class  # type: typing.Type[_T]
    ):
        # type: (...) -> None
        super(ResetObject, self).__init__(wrapped_class())
        self._self_wrapped_class = wrapped_class
        _resetable_objects.add(self)

    def _reset_object(self):
        # type: (...) -> None
        self.__wrapped__ = self._self_wrapped_class()

def Event():
    # type: (...) -> ResetObject[threading.Event]
    return ResetObject(threading.Event)


class PublishQueue(threading.Thread):
    def __init__(
            self,
            interval=2,  # type: float
            target=None,  # type: typing.Callable[[], typing.Any]
            name=None,  # type: typing.Optional[str]
            on_shutdown=None,  # type: typing.Optional[typing.Callable[[], typing.Any]]
    ):
        super(PublishQueue, self).__init__(name=name)
        self._target = target
        self._on_shutdown = on_shutdown
        self.interval = interval
        self.quit = Event()
        self.daemon = False

        # self.manager = multiprocessing.Manager()
        self._creator_pid = os.getpid()
        # q = multiprocessing.Queue()
        # self._queue = self.manager.Queue()
        self._queue = multiprocessing.JoinableQueue()
        self._num_consumers = multiprocessing.Value('d', 0.0)

    def register(self):
        print("Register Queue: {}".format(os.getpid()))
        self._num_consumers.value += 1
        return self._queue

    def run(self):
        while not self.quit.wait(self.interval):
            val = random.randint(0, 500)
            print(f"[{os.getpid()}] QUEUES!!! {self._queue} CONSUMERS {self._num_consumers.value}")
            for _ in range(int(self._num_consumers.value)):
                print(f"PUT {val}")
                self._queue.put(val)
            sleep(2)
        if self._on_shutdown is not None:
            self._on_shutdown()


def worker(q, my_object):
    print("get from queue PID: {}".format(os.getpid()))
    while True:
        try:
            res = q.get(block=False)
            print(f'[{os.getpid()}] Consume {res}')
            my_object.attr_1 = res
            q.task_done()
        except queue.Empty:
            pass
    # for item in iter(q.get, None):
    #     my_object.attr_1 = item
    #     print("got item {} in process {}".format(item, os.getpid()))


def _process_publish_things(master_publisher):
    master_publisher.start()

def publish_things(master_publisher):
    # p = multiprocessing.Process(target=_process_publish_things, args=(master_publisher,))
    p =threading.Thread(target=_process_publish_things, args=(master_publisher,))
    p.start()

master_publisher = PublishQueue()
# publish_things(master_publisher)

class MyClass():
    attr_1 = ""
    attr_2 = ""

my_object = MyClass()


def start_listener():
    global master_publisher
    thr = threading.Thread(target=worker, args=(master_publisher.register(), my_object,))
    thr.start()


if __name__ == "__main__":
    processes = []
    my_object = MyClass()
    thr = threading.Thread(target=worker, args=(master_publisher.register(), my_object,))
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