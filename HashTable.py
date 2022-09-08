from operator import attrgetter
from DeliveryLocation import DeliveryLocation
from PackageAndTruck import Package
import gc


# This class contains two types of Hash Tables to avoid collisions on repetitive key values
class EmptyBucket:
    pass


class LPHashTable:

    def __init__(self, size):
        self.EMPTY_FROM_BEGINNING = EmptyBucket()
        self.EMPTY_AFTER_REMOVAL = EmptyBucket()
        self.table = [self.EMPTY_FROM_BEGINNING] * size

    def insert(self, key, item):
        buckets_checked = 0
        bucket = hash(key) % len(self.table)
        while buckets_checked < len(self.table):
            if type(self.table[bucket]) is EmptyBucket:
                self.table[bucket] = item
                return True
            bucket = (bucket + 1) % len(self.table)
            buckets_checked += 1
        return False

    def search(self, key, desired_data, key_attribute):
        buckets_checked = 0
        bucket = hash(key) % len(self.table)
        attribute = attrgetter(key_attribute)
        while buckets_checked < len(self.table):
            if attribute(self.table[bucket]) == key:
                if desired_data is not None:
                    return getattr(self.table[bucket], desired_data)
                else:
                    return self.table[bucket]
            else:
                bucket = (bucket + 1) % len(self.table)
                buckets_checked += 1
        return None

    def search_and_remove(self, key, desired_data, key_attribute, removeable):
        attribute = attrgetter(key_attribute)
        return_list = self.search(key, desired_data, key_attribute)
        i = 0
        while i < len(return_list):
            if attribute(return_list[i]) in removeable:
                del return_list[i]
                continue
            i += 1
        gc.collect()
        return return_list

    def remove(self, key, key_attribute):
        bucket = hash(key) % len(self.table)
        bucket_checked = 0
        attribute = attrgetter('name')
        while bucket_checked < len(self.table):
            if attribute(self.table[bucket]) == key:
                self.table[bucket] = None
                return True
            else:
                bucket = (bucket + 1) % len(self.table)
                bucket_checked += 1
        return False

    def print_all(self):
        for obj in self.table:
            if type(obj) == DeliveryLocation:
                print(obj.name, '              ',
                      [(location.name, location.distance) for location in obj.location_list],
                      len(obj.location_list))
            elif type(obj) == Package:
                print('ID: %d, Address: %s, Delivery deadline: %s, City: %s, Zip: %s, Weight: %d, Status: %s' % (obj.id, obj.address, obj.delivery_deadline, obj.city, obj.zip, obj.weight, obj.status))
        print()


class ChainingHashTable:

    def __init__(self, size):
        self.table = []
        for i in range(size):
            self.table.append([])

    def insert(self, key, item):
        bucket = hash(key) % len(self.table)
        self.table[bucket].append(item)

    def search(self, key):
        bucket = hash(key) % len(self.table)
        buckets_list = self.table[bucket]
        attribute = attrgetter('address')
        index_list = []
        for item in buckets_list:
            if attribute(item) == key:
                index_list.append(item)
        if len(index_list) > 0:
            return index_list

    def remove(self, key, value=None):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]
        attribute = attrgetter('address')
        for item in bucket_list:
            if value is None:
                if attribute(item) == key:
                    bucket_list.remove(item)
            elif item == value:
                bucket_list.remove(item)
                return True
        return False

    def print_all(self):
        for list in self.table:
            # print(list)
            if len(list) > 0:
                for item in list:
                    print(item.id, item.status)
        print()
