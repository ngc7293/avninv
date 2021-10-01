"""Catalog Service Implementation"""

import grpc

from bson.objectid import ObjectId

from avninv.serde.protobson import bson_to_protobuf, protobuf_to_bson

from avninv.catalog.v1.catalog_pb2_grpc import CatalogServicer
from avninv.catalog.v1.catalog_pb2 import Part


class CatalogService(CatalogServicer):
    def __init__(self, collection):
        self.collection = collection

    def CreatePart(self, request, context):
        bson = protobuf_to_bson(request.part)
        result = self.collection.insert_one(bson)
        bson = self.collection.find_one({"_id": ObjectId(result.inserted_id)})
        part = bson_to_protobuf(bson, Part)
        part.name = f'org/main/parts/{str(bson["_id"])}'
        return part

    def GetPart(self, request, context):
        oid = request.name.split('/')[-1]

        if not ObjectId.is_valid(oid):
            context.abort(grpc.StatusCode(grpc.StatusCode.INVALID_ARGUMENT), 'Invalid ID')

        bson = self.collection.find_one({"_id": ObjectId(oid)})
        if not bson:
            context.abort(grpc.StatusCode(grpc.StatusCode.NOT_FOUND), 'Part not found')

        part = bson_to_protobuf(bson, Part)
        part.name = f'org/main/parts/{str(bson["_id"])}'
        return part
