from bson.objectid import ObjectId


class InvalidOid(ValueError):
    def __init__(self, oid):
        self.oid = oid
        self.message = f'"{oid} is not a valid ObjectId'


class DocumentNotFound(Exception):
    def __init__(self, oid):
        self.oid = oid
        self.message = f'Could not find document with oid "{str(oid)}"'


class Collection:
    def __init__(self, collection):
        self.db = collection

    def _validate_oid(self, oid):
        if not isinstance(oid, ObjectId):
            if not ObjectId.is_valid(oid):
                raise InvalidOid(oid)

            oid = ObjectId(oid)
        return oid

    def update(self, oid, bson):
        oid = self._validate_oid(oid)
        result = self.db.update_one(
            {'_id': oid},
            {
                '$set': bson['$set'],
                '$unset': bson['$unset']
            }
        )

        if result.matched_count == 0:
            raise DocumentNotFound(oid)

        self.db.update_one({'_id': oid}, {'$pull': bson['$pull']})

    def delete(self, oid):
        oid = self._validate_oid(oid)
        result = self.db.delete_one({"_id": oid})

        if result.deleted_count == 0:
            raise DocumentNotFound(oid)

    def insert(self, part):
        return self.db.insert_one(part).inserted_id

    def get(self, oid):
        oid = self._validate_oid(oid)
        bson = self.db.find_one({"_id": oid})
        if not bson:
            raise DocumentNotFound(oid)
        return bson

    def list(self):
        return self.db.find()
