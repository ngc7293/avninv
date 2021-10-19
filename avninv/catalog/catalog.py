"""Catalog Service Implementation"""

from google.protobuf.empty_pb2 import Empty

from avninv.catalog.parts_collection import PartCollection
from avninv.catalog.v1.catalog_pb2 import ListPartResponse, Part
from avninv.catalog.v1.catalog_pb2_grpc import CatalogServicer
from avninv.error.api_error import ApiError, StatusCode
from avninv.serde.protobson import bson_to_protobuf, protobuf_to_bson, protobuf_to_update_document


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
            part.name = f'orgs/main/parts/{str(bson["_id"])}'
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
            part.name = f'orgs/main/parts/{str(bson["_id"])}'
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
                part.name = f'orgs/main/parts/{str(bson["_id"])}'
                parts.append(part)
            return ListPartResponse(parts=parts)
        except ApiError as err:
            context.abort(err.status, err.message)

    def UpdatePart(self, request, context):
        try:
            _, oid = self._validate_name(request.name, require_org='main')
            bson = protobuf_to_update_document(request.part, fields_mask=request.update_mask.paths)
            self.collection.update(oid, bson)
            bson = self.collection.get(oid)
            part = bson_to_protobuf(bson, Part)
            part.name = f'orgs/main/parts/{str(bson["_id"])}'
            return part
        except ApiError as err:
            context.abort(err.status, err.message)

    @staticmethod
    def _validate_path(tokens, hierarchy):
        if len(tokens) != len(hierarchy):
            return False, None
        for depth, (expected, actual) in enumerate(zip(hierarchy, tokens)):
            if expected and actual != expected:
                return False, depth
        return True, None

    @staticmethod
    def _validate_parent(parent, require_org=None):
        tokens = parent.split('/')
        valid, _ = CatalogService._validate_path(tokens, ['orgs', require_org, 'parts'])
        
        if not valid:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid parent')
        return tokens[1]

    @staticmethod
    def _validate_name(name, require_org=None):
        tokens = name.split('/')
        valid, _ = CatalogService._validate_path(tokens, ['orgs', require_org, 'parts', None])
        
        if not valid:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid name')
        return tokens[1], tokens[3]
        
