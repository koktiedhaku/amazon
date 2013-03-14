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

            print "Put %s" % (cur_item)
            self.outqueue.put(cur_item)
            self.inqueue.task_done()

class MultiFetch(threading.Thread):
    def __init__(self, outq):
        threading.Thread.__init__(self)
        self.outqueue = outq

    def run(self):
        while True:
            cur_item = self.outqueue.get()
            
            print "Get %s" % (cur_item)
            self.outqueue.task_done()

class QueueWorker:
    def __init__(self, inq = Queue.Queue(), outq = Queue.Queue()):
        self.inqueue = inq
        self.outqueue = outq
        self.linklist = list() # Alloc a new one, not a pointer to the existing one

    def loadLinks(self, linklst):
        for item in range(len(linklst)):
            t = FeedQueue(self.inqueue, self.outqueue)
            t.daemon = True
            t.start()
        for item in linklst:
            self.inqueue.put(item)
        self.linklist = linklst

    def processLinkQueue(self):
        for item in range(len(self.linklist)):
            t = MultiFetch(self.outqueue)
            t.daemon = True
            t.start()
        self.inqueue.join()
        self.outqueue.join()

if __name__ == '__main__':
    links = [
    '&pageNumber=69&showViewpoints=0',
    '&pageNumber=70&showViewpoints=0',
    '&pageNumber=71&showViewpoints=0',
    '&pageNumber=72&showViewpoints=0',
    '&pageNumber=73&showViewpoints=0',
    '&pageNumber=74&showViewpoints=0',
    '&pageNumber=75&showViewpoints=0',
    '&pageNumber=76&showViewpoints=0',
    '&pageNumber=77&showViewpoints=0',
    '&pageNumber=78&showViewpoints=0',
    '&pageNumber=79&showViewpoints=0',
    '&pageNumber=80&showViewpoints=0',
    '&pageNumber=81&showViewpoints=0',
    '&pageNumber=82&showViewpoints=0',
    '&pageNumber=83&showViewpoints=0',
    '&pageNumber=84&showViewpoints=0',
    '&pageNumber=85&showViewpoints=0']
    q = QueueWorker()
    q.loadLinks(links)
    q.processLinkQueue()
#    item_list = ['item1', 'item2', 'item3']
#    inqueue = Queue.Queue()
#    outqueue = Queue.Queue()
#
#    for item in range(len(item_list)):
#        t = FeedQueue(inqueue, outqueue)
#        t.daemon = True
#        t.start()
#
#    for item in item_list:
#        inqueue.put(item)
#
#    for item in range(len(item_list)):
#        t = MultiFetch(outqueue)
#        t.daemon = True
#        t.start()
#
#    inqueue.join()
#    outqueue.join()

