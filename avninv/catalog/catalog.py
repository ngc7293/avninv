"""Catalog Service Implementation"""

from bson.objectid import ObjectId

from avninv.rpc.status import StatusCode, rpc_status
from avninv.serde.protobson import bson_to_protobuf, protobuf_to_bson

from avninv.catalog.catalog_pb2_grpc import CatalogServicer
from avninv.catalog.catalog_pb2 import AddPartResponse, GetPartResponse, PartDetails


class CatalogService(CatalogServicer):
    def __init__(self, collection):
        self.collection = collection

    def AddPart(self, request, context):
        try:
            bson = protobuf_to_bson(request.details)
            result = self.collection.insert(bson)
            return AddPartResponse(id=str(result))
        except Exception as e:
            print(e)
            context.abort_with_status(rpc_status(StatusCode.INTERNAL))

    def GetPart(self, request, context):
        try:
            bson = self.collection.find_one({"_id": ObjectId(request.id)})
            if not bson:
                context.abort_with_status(rpc_status(StatusCode.NOT_FOUND))
            return GetPartResponse(details=bson_to_protobuf(bson, PartDetails))
        except Exception as e:
            print(e)
            context.abort_with_status(rpc_status(StatusCode.INTERNAL))
