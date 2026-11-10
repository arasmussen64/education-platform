def string_hash(key):
    """A hash function you can see: mix each character in, wrapping at 2**32."""
    h = 0
    for ch in key:
        h = (h * 31 + ord(ch)) % 2**32
    return h


class HashTable:
    """A dict built by hand: a list of buckets, each a short list of (key, value) pairs."""

    def __init__(self, hash_function=string_hash):
        self.hash_function = hash_function
        self.buckets = [[] for _ in range(4)]
        self.count = 0
        self.compared = 0

    def bucket_for(self, key):
        return self.buckets[self.hash_function(key) % len(self.buckets)]

    def get(self, key):
        for stored_key, value in self.bucket_for(key):
            self.compared += 1
            if stored_key == key:
                return value
        raise KeyError(key)

    def put(self, key, value):
        bucket = self.bucket_for(key)
        for i, (stored_key, _) in enumerate(bucket):
            self.compared += 1
            if stored_key == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.count += 1
        if self.count > 2 * len(self.buckets) // 3:
            self.grow()

    def grow(self):
        pairs = [pair for bucket in self.buckets for pair in bucket]
        self.buckets = [[] for _ in range(2 * len(self.buckets))]
        for key, value in pairs:
            self.bucket_for(key).append((key, value))


names = [f"user{i}" for i in range(1000)]

table = HashTable()
for i, name in enumerate(names):
    table.put(name, i)
table.compared = 0
for name in names:
    table.get(name)
print("good hash:", len(table.buckets), "buckets, longest", max(len(b) for b in table.buckets), "| 1000 lookups:", table.compared, "comparisons")

bad = HashTable(hash_function=len)
for i, name in enumerate(names):
    bad.put(name, i)
bad.compared = 0
for name in names:
    bad.get(name)
print("bad hash:", len(bad.buckets), "buckets, longest", max(len(b) for b in bad.buckets), "| 1000 lookups:", bad.compared, "comparisons")

compared = 0
for name in names:
    for candidate in names:
        compared += 1
        if candidate == name:
            break
print("list scans: 1000 lookups:", compared, "comparisons")

real = {name: i for i, name in enumerate(names)}
print("Python's dict agrees:", all(real[name] == table.get(name) for name in names))
