class PeekIter:
    def __init__(self, data):
        self.iter = iter(data)
        self.peeked_list = []

    def __next__(self):
        if len(self.peeked_list) > 0:
            value = self.peeked_list[0]
            self.peeked_list = self.peeked_list[1:]

            return value
        else:
            return next(self.iter)

    def peek(self, offset=0):
        while not len(self.peeked_list) > offset:  
            self.peeked_list.append(next(self.iter))
        
        return self.peeked_list[offset]

    def __iter__(self):
        return self

def check_integer(data):
    num_chars = [str(i) for i in range(10)]

    for c in data:
        if not c in num_chars:
            return False

    return True


def check_float(data):
    num_chars = [str(i) for i in range(10)]

    count = 0

    for c in data:
        if c == ".":
            if count == 0:
                count += 1
                continue
            else:
                return False
        if not c in num_chars:
            return False

    return True


def compare(str0, str1):
    SIZE = 60

    str0, str1 = str(str0), str(str1)
    lines0, lines1 = str0.split("\n"), str1.split("\n")
    if len(lines0) < len(lines1):
        lines0 += [""]* (len(lines1) - len(lines0))
    else:
        lines1 += [""]* (len(lines0) - len(lines1))

    for l0, l1 in zip(lines0, lines1):
        print(l0.ljust(SIZE), "|", l1)


def get_size_of_type(t):
    if t.endswith("*"):
        return 4
    elif "int" in t:
        return 4
    elif "short" in t:
        return 2
    elif "char" in t:
        return 1
    elif "void" in t:
        return 0

def get_next(v, to_remove, maximum):
    while v in to_remove and v < maximum:
        v += 1
    
    return v
