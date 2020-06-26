from functools import wraps
from itertools import islice
from queue import Queue


class ConversionGraph:

    def __init__(self):
        self._graph = {}

    def register(self, src, tgt):
        def decorator(func):
            self._graph.setdefault(src, {})[tgt] = func
            self._graph.setdefault(tgt, {})
            return func
        return decorator

    def find_path(self, src, tgt):
        if src == tgt:
            return ()

        paths = {src: (src,)}
        queue = Queue()
        queue.put(src)

        while not queue.empty():
            node = queue.get()
            for neighbor in self._graph[node]:
                if neighbor not in paths:
                    paths[neighbor] = (*paths[node], neighbor)
                    queue.put(neighbor)
                if neighbor == tgt:
                    return paths[neighbor]

        raise ValueError(f'Unable to find a conversion path {src} -> {tgt}')

    def __call__(self, src, tgt, srcval):
        path = self.find_path(src, tgt)
        for a, b in zip(path, islice(path, 1, None)):
            srcval = self._graph[a][b](srcval)
        return srcval
