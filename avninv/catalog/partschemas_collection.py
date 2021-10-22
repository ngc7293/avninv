import logging

from pymongo.errors import PyMongoError

from avninv.catalog.v1.catalog_pb2 import PartSchema
from avninv.catalog.collection import Collection, DocumentNotFound, InvalidOid
from avninv.error.api_error import ApiError, StatusCode
from avninv.serde.protobson import (
    protobuf_to_bson, protobuf_to_update_document, bson_to_protobuf
)


class PartSchemaCollection:
    def __init__(self, collection):
        self.collection = Collection(collection)

    def _safe_execute(self, method, *args, **kwargs):
        try:
            return method(*args, **kwargs)

        except DocumentNotFound:
            raise ApiError(StatusCode.NOT_FOUND, 'No such schema')

        except InvalidOid:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid name')

        except PyMongoError as err:
            logging.error(f'error updating part schema: {str(err)}')
            raise ApiError(StatusCode.INTERNAL, 'Internal error')

    def update(self, oid, schema, fields_mask):
        bson = protobuf_to_update_document(schema, fields_mask)
        self._safe_execute(self.collection.update, oid, bson)

    def delete(self, oid):
        self._safe_execute(self.collection.delete, oid)

    def insert(self, schema):
        schema.name = ''
        bson = protobuf_to_bson(schema)
        return self._safe_execute(self.collection.insert, bson)

    def get(self, oid):
        bson = self._safe_execute(self.collection.get, oid)
        schema = bson_to_protobuf(bson, PartSchema)
        schema.name = f'orgs/main/partschemas/{str(bson["_id"])}'
        return schema

    def list(self):
        bsons = self._safe_execute(self.collection.list)

        for bson in bsons:
            schema = bson_to_protobuf(bson, PartSchema)
            schema.name = f'orgs/main/partschemas/{str(bson["_id"])}'
            yield schema
