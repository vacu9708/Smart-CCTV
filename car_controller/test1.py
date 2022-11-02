import multiprocessing as mp
import time

class My_class:
    def __init__(self) -> None:
        self.a=[False]

output=My_class()

def foo(output):
    output.a[0]=True
print(output.a)
foo(output)
print(output.a)