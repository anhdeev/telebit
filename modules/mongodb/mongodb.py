#!/usr/bin/env python
import logging
from pymongo import MongoClient


class Database(object):
    def __init__(self, db):
        self.db_connection = MongoClient("mongodb://127.0.0.1:27017")
        self.db = self.db_connection[db]

    def find(self):
        return self.db[coll].find()

    def find_one(self, coll, cond):
        if cond:
            return self.db[coll].find_one(cond)
        else:
            return self.db[coll].find_one()

    def insert_one(self, coll, obj):
        return self.db[coll].insert_one(obj)

    def update(self, coll, filt, obj):
        logging.debug("Updating collection %s:%s" % (coll, filt))
        update_obj = { '$set': obj }
        return self.db[coll].update_one(filt, update_obj, True)

    def close(self):
        self.db_connection.close()

