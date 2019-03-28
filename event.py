class Event:
    def __init__(self, req):
        self.req = req

    def __lt__(self, other):
        return self.req.graph['time'] < other.req.graph['time']
