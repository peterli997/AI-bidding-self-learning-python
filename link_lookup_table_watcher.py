import pickle
# from collections import Counter
LINK_LEVEL = 7 # number of remaining tricks to be stored - 1
HASH_MOD = [64,65536,536870912,8589934592,4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904]
DETAILED_LINK_OBJ = False # if links are stored

class SuitLink:
    def __init__(self, link):
        if DETAILED_LINK_OBJ:
            self.compressed_link = list(filter(lambda x: x != -1, link))
            self.cache_hash = self.hashing(self.compressed_link)
        else:
            compressed_link = list(filter(lambda x: x != -1, link))
            self.cache_hash = self.hashing(compressed_link)

    def __str__(self):
        return str(self.compressed_link) if DETAILED_LINK_OBJ else str(self.cache_hash)

    @staticmethod
    def hashing(comp_link):
        hashed = 0
        for i in comp_link:
            hashed = hashed * 4 + i
        return hashed * 17 + len(comp_link) - 1

    def __hash__(self):  # different hash => different link
        return self.cache_hash

    def __eq__(self, other):
        return self.cache_hash == other.cache_hash

    def __bool__(self):
        return self.cache_hash != -1

    def __len__(self):
        return (self.cache_hash+1) % 17


class SuitLevelLinks:
    def __init__(self, link_dict, trump, leader=0):
        if leader != 0:
            links = []
            link_trump = SuitLink([])
            for i, link in link_dict.items():
                if i == trump - 1:
                    link_trump = SuitLink([(x - leader) % 4 for x in link if x != -1])
                elif link != [-1] * 13:
                    links.append(SuitLink([(x - leader) % 4 for x in link if x != -1]))
        else:
            links = [SuitLink(y) for x, y in link_dict.items() if x != trump - 1 and y != [-1] * 13]
            link_trump = SuitLink(link_dict[trump-1]) if trump != 5 else SuitLink([])
        if DETAILED_LINK_OBJ:
            self.links = (links, link_trump)
        self.cache_links_hash = (sorted([x.__hash__() for x in links]), link_trump.__hash__())
        self.cache_hash = self.hashing(self.cache_links_hash)
        # assert len(self) % 4 == 0

    def __str__(self):
        if DETAILED_LINK_OBJ:
            result = "{"
            for i in self.links[0]:
                result += str(i)
                result += ', '
            result += '}'
            return result + " trump:" + str(self.links[1])
        else:
            return str(self.cache_links_hash)

    @staticmethod
    def hashing(links_hash):
        hashed = links_hash[1]
        for i in links_hash[0]:
            hashed = (hashed * 1140850699 + i) % HASH_MOD[LINK_LEVEL]  # it is a prime above max hash of link
        return hashed

    def __hash__(self):
        return self.cache_hash

    def __eq__(self, other):
        if self.cache_hash != other.cache_hash:
            return False
        return self.cache_links_hash == other.cache_links_hash

    def __len__(self):
        result = 0
        for i in self.cache_links_hash[0]:
            result += (i+1) % 17
        return result + (1 + self.cache_links_hash[1]) % 17


def main(file):
    link_lookup_table = pickle.load(file)
    it = iter(link_lookup_table)
    count = 0
    complete_count = 0
    while True:
        try:
            a = it.__next__()
            complete_count += 1
            print(a)
            if complete_count >= 500:
                continue

        except StopIteration:
            break
    print(count, complete_count)


if DETAILED_LINK_OBJ:
    with open("detailed_link_lookup_table.pkl", 'rb') as file:
        main(file)
else:
    with open("compressed_link_lookup_table.pkl", 'rb') as file:
        main(file)



