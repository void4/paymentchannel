import os
import pickle

class PersistentStore:
    """
    Uses the pickle module to store a dictionary data structure permanently on disk.
    It should only be used with trusted data.
    """
    def __init__(self, dbpath="signatures.db"):
        
        self.dbpath = dbpath
        db = self.load()
        self.store(db)

    def load(self):
        """Loads the database to its filepath and initialises an empty database if it does not exist"""
        if not os.path.exists(self.dbpath):
            open(self.dbpath, "w+").close()
        if os.path.getsize(self.dbpath) > 0: 
            try:
                with open(self.dbpath, "rb") as dbfile:
                    db = pickle.load(dbfile)
                    if not db:
                        db = {}
            except IOError:
                db = {}
        else:
            db = {}
        return db

    def store(self, db):
        """Writes the database to its filepath"""
        with open(self.dbpath, "wb+") as dbfile:
            pickle.dump(db, dbfile)

    def get(self, key):
        """Get data for given store key. Raise hug.exceptions.StoreKeyNotFound if key does not exist."""
        db = self.load()
        try:
            return db[key]
        except KeyError:
            raise StoreKeyNotFound(key)

    def getn(self, key):
        db = self.load()
        try:
            return db[key]
        except KeyError:
            return None

    def exists(self, key):
        """Return whether key exists or not."""
        db = self.load()
        return key in db

    def set(self, key, data):
        """Set data object for given store key."""
        db = self.load()
        db[key] = data
        self.store(db)

    def delete(self, key):
        """Delete data for given store key."""
        db = self.load()
        del db[key]
        self.store(db)