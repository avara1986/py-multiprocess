# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os

from main import func


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    print("I am print_hi process:")
    print("print_hi ID:", os.getpid())
    print("Parent's process ID:", os.getppid())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    func()
    print_hi("la")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
