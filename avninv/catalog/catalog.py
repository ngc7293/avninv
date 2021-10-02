"""Catalog Service Implementation"""

from google.protobuf.empty_pb2 import Empty

from avninv.catalog.parts_collection import PartCollection
from avninv.catalog.v1.catalog_pb2 import ListPartResponse, Part
from avninv.catalog.v1.catalog_pb2_grpc import CatalogServicer
from avninv.error.api_error import ApiError, StatusCode
from avninv.serde.protobson import bson_to_protobuf, protobuf_to_bson


class CatalogService(CatalogServicer):
    def __init__(self, collection):
        self.collection = PartCollection(collection)

    def CreatePart(self, request, context):
        try:
            self._validate_parent(request.parent, require_org='main')
            request.part.name = ''
            bson = protobuf_to_bson(request.part)
            id = self.collection.insert(bson)
            bson = self.collection.get(id)
            part = bson_to_protobuf(bson, Part)
            part.name = f'org/main/parts/{str(bson["_id"])}'
            return part
        except ApiError as err:
            context.abort(err.status, err.message)

    def DeletePart(self, request, context):
        try:
            _, oid = self._validate_name(request.name, require_org='main')
            self.collection.delete(oid)
            return Empty()
        except ApiError as err:
            context.abort(err.status, err.message)

    def GetPart(self, request, context):
        try:
            _, oid = self._validate_name(request.name, require_org='main')
            bson = self.collection.get(oid)
            part = bson_to_protobuf(bson, Part)
            part.name = f'org/main/parts/{str(bson["_id"])}'
            return part
        except ApiError as err:
            context.abort(err.status, err.message)

    def ListParts(self, request, context):
        try:
            self._validate_parent(request.parent, require_org='main')
            bsons = self.collection.list()
            parts = []
            for bson in bsons:
                part = bson_to_protobuf(bson, Part)
                part.name = f'org/main/parts/{str(bson["_id"])}'
                parts.append(part)
            return ListPartResponse(parts=parts)
        except ApiError as err:
            context.abort(err.status, err.message)

    def UpdatePart(self, request, context):
        return super().UpdatePart(request, context)

    def _validate_parent(self, parent, require_org=None):
        tokens = parent.split('/')
        if len(tokens) != 3:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid parent')

        tok1, org, tok2 = tokens
        if tok1 != 'org' or tok2 != 'parts':
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid parent')

        if require_org and org != require_org:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid organization')
        return org

    def _validate_name(self, name, require_org=None):
        tokens = name.split('/')
        if len(tokens) != 4:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid parent')

        tok1, org, tok2, name = tokens
        if tok1 != 'org' or tok2 != 'parts':
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid name')

        if require_org and org != require_org:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid organization')
        return org, name
