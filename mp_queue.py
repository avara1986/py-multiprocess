# SuperFastPython.com
# example of using a pipe between processes
from time import sleep
from random import random
from multiprocessing import Process
from multiprocessing import Pipe
from  multiprocessing.connection import Connection

# generate work
def sender(connection):
    print('Sender: Running', flush=True)
    # generate work
    for i in range(10):
        # generate a value
        value = random()
        # block
        sleep(value)
        # send data
        connection.send(value)
    # all done
    connection.send(None)
    print('Sender: Done', flush=True)


# consume work
def receiver(name, connection):
    print(f'[{name}] Receiver: Running', flush=True)
    # consume work
    while True:
        # get a unit of work
        item = connection.recv()
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
    sender_process = Process(target=sender, args=(conn2,))
    sender_process.start()
    # start the receiver
    receiver_process = Process(target=receiver, args=("conn1", conn1,))
    receiver_process4 = Process(target=receiver, args=("conn4", conn1,))
    receiver_process.start()
    # # wait for all processes to finish
    conn3 = Connection()
    receiver("conn3", conn3)
    sender_process.join()
    receiver_process.join()
    receiver_process4.join()