class PeekIter:
    def __init__(self, data):
        self.iter = iter(data)
        self.ptr = 0

        self.peeked_list = []

    def __next__(self):
        if len(self.peeked_list) > 0:
            value = self.peeked_list[len(self.peeked_list) - 1]
            self.peeked_list = self.peeked_list[:-1]

            return value
        else:
            return next(self.iter)

    def peek(self):
        if len(self.peeked_list) > 0:
            return self.peeked_list[len(self.peeked_list) - 1]
        self.peeked_list.append(next(self.iter))
        return self.peeked_list[len(self.peeked_list) - 1]

    def __iter__(self):
        return self
