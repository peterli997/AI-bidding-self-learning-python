import pickle
LINK_LEVEL = 7 # number of remaining tricks to be stored - 1
HASH_MOD = [64,65536,536870912,8589934592,4611686018427387904,4611686018427387904,4611686018427387904,4611686018427387904]


class SuitLink:
    def __init__(self, link):
        self.compressed_link = list(filter(lambda x: x != -1, link))
        self.cache_valid = False
        self.cache_hash = self.__hash__()
        self.cache_valid = True

    def __str__(self):
        return str(self.compressed_link)

    def __hash__(self):  # different hash => different link
        if self.cache_valid:
            return self.cache_hash
        hashed = 0
        for i in self.compressed_link:
            if i != -1:
                hashed = hashed * 4 + i
        self.cache_hash = hashed * 13 + len(self.compressed_link) - 1
        self.cache_valid = True
        return self.cache_hash

    def __eq__(self, other):
        if self.cache_valid and other.cache_valid:
            if self.cache_hash == other.cache_hash:
                assert self.compressed_link == other.compressed_link
                return True
            else:
                assert self.compressed_link != other.compressed_link
                return False
        else:
            return self.compressed_link == other.compressed_link


class SuitLevelLinks:
    def __init__(self, link_dict, trump, leader=0):
        self.cache_valid = False
        self.trump = trump
        if leader != 0:
            self.link_dict = set()
            for i, link in link_dict.items():
                if i == trump - 1:
                    self.link_trump = SuitLink([(x - leader) % 4 for x in link if x != -1])
                else:
                    self.link_dict.add(SuitLink([(x - leader) % 4 for x in link if x != -1]))
        else:
            self.link_dict = {SuitLink(y) for x, y in link_dict.items() if x != trump - 1}
            if trump != 5:
                self.link_trump = SuitLink(link_dict[trump-1])
        self.cache_link_hash = {x.__hash__() for x in self.link_dict}  # need to be alwsys valid
        if trump != 5:
            self.cache_trump_hash = self.link_trump.__hash__()  # need to be always valid
        self.cache_hash = self.__hash__()
        self.cache_valid = True

    def __str__(self):
        return str(self.link_dict) + str(self.trump) + "" if self.trump == 5 else str(self.link_trump)

    def __hash__(self):
        if self.cache_valid:
            return self.cache_hash
        else:
            hashed = 0
            if self.trump != 5:
                hashed += self.cache_trump_hash
            for i in sorted(self.cache_link_hash):
                hashed = (hashed * 872415239 + i) % HASH_MOD[LINK_LEVEL]  # it is a prime above max hash of link
            if self.trump == 5:
                hashed *= 3
            self.cache_hash = hashed
            self.cache_valid = True
            return hashed

    def __eq__(self, other):
        if self.trump != other.trump:
            return False
        if self.cache_valid and other.cache_valid and self.cache_hash != other.cache_hash:
            return False
        if self.cache_link_hash != other.cache_link_hash:
            return False
        if self.trump != 5:
            if self.cache_trump_hash != other.cache_trump_hash:
                return False
        return True

with open("link_lookup_table.pkl", 'rb') as f:
    link_lookup_table = pickle.load(f)
    it = iter(link_lookup_table)
    print(len(link_lookup_table))
