class RequestIterator:

    def __init__(self, queue):
        self._queue = queue
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._queue):
            item = self._queue[self._index]
            self._index += 1
            return item
        raise StopIteration
