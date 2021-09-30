"""Catalog Service Implementation"""

import grpc

from bson.objectid import ObjectId

from avninv.serde.protobson import bson_to_protobuf, protobuf_to_bson

from avninv.catalog.proto.catalog_pb2_grpc import CatalogServicer
from avninv.catalog.proto.catalog_pb2 import AddPartResponse, GetPartResponse, PartDetails


class CatalogService(CatalogServicer):
    def __init__(self, collection):
        self.collection = collection

    def AddPart(self, request, context):
        bson = protobuf_to_bson(request.details)
        result = self.collection.insert_one(bson)
        return AddPartResponse(id=str(result.inserted_id))

    def GetPart(self, request, context):
        if not ObjectId.is_valid(request.id):
            context.abort(grpc.StatusCode(grpc.StatusCode.INVALID_ARGUMENT), 'Invalid ID')

        bson = self.collection.find_one({"_id": ObjectId(request.id)})
        if not bson:
            context.abort(grpc.StatusCode(grpc.StatusCode.NOT_FOUND), 'Part not found')

        return GetPartResponse(details=bson_to_protobuf(bson, PartDetails))
