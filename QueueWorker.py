import threading
import Queue

class FeedQueue(threading.Thread):
    def __init__(self, inq, outq):
        threading.Thread.__init__(self)
        self.inqueue = inq
        self.outqueue = outq

    def run(self):
        while True:
            cur_item = self.inqueue.get()

            result = 'blaa'
            self.outqueue.put(result)
            self.inqueue.task_done()

class MultiFetch(threading.Thread):
    def __init__(self, outq):
        threading.Thread.__init__(self)
        self.outqueue = outq

    def run(self):
        while True:
            item = self.outqueue.get()
            
            result = 'Hommat hanskattu'
            self.outqueue.task_done()

if __name__ == '__main__':
    item_list = ['item1', 'item2', 'item3']
    inqueue = Queue.Queue()
    outqueue = Queue.Queue()

    for item in range(len(item_list)):
        t = FeedQueue(inqueue, outqueue)
        t.daemon = True
        t.start()

    for item in item_list:
        inqueue.put(item)

    for item in range(len(item_list)):
        t = MultiFetch(outqueue)
        t.daemon = True
        t.start()

    inqueue.join()
    outqueue.join()

