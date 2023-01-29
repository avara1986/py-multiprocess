# SuperFastPython.com
# example of using a pipe between processes
from time import sleep
from random import random
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Pipe
from  multiprocessing.connection import Connection

# generate work
def sender(queue_1):
    print('Sender: Running', flush=True)
    # generate work
    for i in range(10):
        # generate a value
        value = random()
        # block
        sleep(value)
        # send data
        queue_1.put(f'hello {value}')
    # all done
    queue_1.send(None)
    print('Sender: Done', flush=True)


# consume work
def receiver(name, queue_1):
    print(f'[{name}] Receiver: Running', flush=True)
    # consume work
    while True:
        # get a unit of work
        item = queue_1.get()
        # report
        print(f'[{name}] > receiver got {item}', flush=True)
        # check for stop
        if item is None:
            break
    # all done
    print(f'[{name}] > Receiver: Done', flush=True)


# entry point
if __name__ == '__main__':
    # create the pipe
    conn1, conn2 = Pipe()
    # start the sender
    queue_1 = Queue()
    sender_process = Process(target=sender, args=(queue_1,))
    sender_process.start()
    # start the receiver
    receiver_process = Process(target=receiver, args=("conn1", queue_1,))
    receiver_process4 = Process(target=receiver, args=("conn4", queue_1,))
    receiver_process.start()
    # # wait for all processes to finish
    receiver("conn3", queue_1)
    sender_process.join()
    receiver_process.join()
    receiver_process4.join()