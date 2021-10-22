"""Catalog Service Implementation"""

import logging

from google.protobuf.empty_pb2 import Empty

from avninv.catalog.parts_collection import PartCollection
from avninv.catalog.partschemas_collection import PartSchemaCollection
from avninv.catalog.v1.catalog_pb2 import GetPartSchemaRequest, ListPartResponse, ListPartSchemaResponse
from avninv.catalog.v1.catalog_pb2_grpc import CatalogServicer
from avninv.error.api_error import ApiError, StatusCode


class CatalogService(CatalogServicer):
    def __init__(self, parts, schemas):
        self.parts = PartCollection(parts)
        self.schemas = PartSchemaCollection(schemas)

    def CreatePart(self, request, context):
        try:
            self._validate_parent(request.parent, 'parts', require_org='main')
            schema = self.GetPartSchema(GetPartSchemaRequest(name=request.part.schema_name), context)
            id = self.parts.insert(request.part)
            return self.parts.get(id)
        except ApiError as err:
            context.abort(err.status, err.message)

    def DeletePart(self, request, context):
        try:
            _, oid = self._validate_name(request.name, 'parts', require_org='main')
            self.parts.delete(oid)
            return Empty()
        except ApiError as err:
            context.abort(err.status, err.message)

    def GetPart(self, request, context):
        try:
            _, oid = self._validate_name(request.name, 'parts', require_org='main')
            return self.parts.get(oid)
        except ApiError as err:
            context.abort(err.status, err.message)

    def ListParts(self, request, context):
        try:
            self._validate_parent(request.parent, 'parts', require_org='main')
            parts = list(self.parts.list())
            return ListPartResponse(parts=parts)
        except ApiError as err:
            context.abort(err.status, err.message)

    def UpdatePart(self, request, context):
        try:
            _, oid = self._validate_name(request.name, 'parts', require_org='main')
            part = self.parts.get(oid)
            schema = self.GetPartSchema(GetPartSchemaRequest(name=request.part.schema_name or part.schema_name), context)
            self.parts.update(oid, request.part, fields_mask=request.update_mask.paths)
            return self.parts.get(oid)
        except ApiError as err:
            context.abort(err.status, err.message)

    def CreatePartSchema(self, request, context):
        try:
            self._validate_parent(request.parent, 'partschemas', require_org='main')
            id = self.schemas.insert(request.schema)
            return self.schemas.get(id)
        except ApiError as err:
            context.abort(err.status, err.message)
        except Exception as err:
            logging.error(err)
            context.abort(StatusCode.INTERNAL, err)

    def DeletePartSchema(self, request, context):
        try:
            _, oid = self._validate_name(request.name, 'partschemas', require_org='main')
            self.schemas.delete(oid)
            return Empty()
        except ApiError as err:
            context.abort(err.status, err.message)

    def GetPartSchema(self, request, context):
        try:
            _, oid = self._validate_name(request.name, 'partschemas', require_org='main')
            return self.schemas.get(oid)
        except ApiError as err:
            context.abort(err.status, err.message)

    def ListPartSchemas(self, request, context):
        try:
            self._validate_parent(request.parent, 'partschemas', require_org='main')
            schemas = list(self.schemas.list())
            return ListPartSchemaResponse(schemas=schemas)
        except ApiError as err:
            context.abort(err.status, err.message)

    def UpdatePartSchema(self, request, context):
        try:
            _, oid = self._validate_name(request.name, 'partschemas', require_org='main')
            self.schemas.update(oid, request.schema, fields_mask=request.update_mask.paths)
            return self.schemas.get(oid)
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
    def _validate_parent(parent, collection, require_org=None):
        tokens = parent.split('/')
        valid, _ = CatalogService._validate_path(tokens, ['orgs', require_org, collection])

        if not valid:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid parent')
        return tokens[1]

    @staticmethod
    def _validate_name(name, collection, require_org=None):
        tokens = name.split('/')
        valid, _ = CatalogService._validate_path(tokens, ['orgs', require_org, collection, None])

        if not valid:
            raise ApiError(StatusCode.INVALID_ARGUMENT, 'Invalid name')
        return tokens[1], tokens[3]
