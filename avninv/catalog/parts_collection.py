from sys import stderr

from avninv.error.api_error import ApiError, StatusCode
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError


class PartCollection:
    def __init__(self, collection):
        self.db = collection

    def _validate_oid(self, oid):
        if not isinstance(oid, ObjectId):
            if not ObjectId.is_valid(oid):
                raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid ID')
            oid = ObjectId(oid)
        return oid

    def delete(self, oid):
        oid = self._validate_oid(oid)
        try:
            result = self.db.delete_one({"_id": oid})
            if result.deleted_count == 0:
                raise ApiError(StatusCode.NOT_FOUND, 'No such part')

        except PyMongoError as err:
            print(f'error deleting part: {str(err)}', file=stderr)
            raise ApiError(StatusCode.INTERNAL, 'Internal error')

    def insert(self, part):
        if '_id' in part:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'ID is not allowed in Create call')

        try:
            result = self.db.insert_one(part)
            return result.inserted_id

        except PyMongoError as err:
            print(f'error inserting part: {str(err)}', file=stderr)
            raise ApiError(StatusCode.INTERNAL, 'Internal error')

    def get(self, oid):
        oid = self._validate_oid(oid)

        try:
            bson = self.db.find_one({"_id": oid})
            if not bson:
                raise ApiError(StatusCode.NOT_FOUND, 'No such part')
            return bson

        except PyMongoError as err:
            print(f'error fetching part: {str(err)}', file=stderr)
            raise ApiError(StatusCode.INTERNAL, 'Internal error')

    def list(self):
        try:
            return self.db.find()
        except PyMongoError as err:
            print(f'error fetching parts: {str(err)}', file=stderr)
            raise ApiError(StatusCode.INTERNAL, 'Internal error')
