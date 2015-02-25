'''This CountDownLatch is used to solve multithreading concurrency problem while crawling the proxies and check them,
which is pretty much like the producer-consumer problem. The CountDownLatch works like what is in Java.'''

import threading

class CountDownLatch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        self.lock.acquire()
#         print("count_down get lock " + threading.currentThread().getName())
        self.count -= 1
        if self.count <= 0:
            self.lock.notifyAll()
#         print("count_down release lock " + threading.currentThread().getName())
        self.lock.release()

    def await(self):
        self.lock.acquire()
#         print("await get lock "+ threading.currentThread().getName())
        while self.count > 0:
            self.lock.wait()
#         print("await release lock "+ threading.currentThread().getName())
        self.lock.release()