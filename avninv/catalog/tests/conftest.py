import concurrent.futures
import uuid
import os
import random

import grpc
import pymongo
import pytest
import yaml

from avninv.catalog.catalog import CatalogService
from avninv.catalog.v1.catalog_pb2 import PartSchema, PartAttributeSchema, CreatePartSchemaRequest
from avninv.catalog.v1.catalog_pb2_grpc import add_CatalogServicer_to_server, CatalogStub


class ConfigNotFoundException(Exception):
    pass


def _get_config():
    paths = ['etc/config.test.yaml', 'etc/config.test.ci.yaml']
    for path in paths:
        if os.path.isfile(path):
            return open(path, 'r')
    raise ConfigNotFoundException


@pytest.fixture
def service():
    config = yaml.load(_get_config(), Loader=yaml.CLoader)
    client = pymongo.MongoClient(config['database'][0], serverSelectionTimeoutMS=1000)
    parts_collection = str(uuid.uuid4())
    schemas_collection = str(uuid.uuid4())

    client['catalog-test'].create_collection(parts_collection)
    client['catalog-test'].create_collection(schemas_collection)

    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=1))
    add_CatalogServicer_to_server(
        CatalogService(
            client['catalog-test'][parts_collection],
            client['catalog-test'][schemas_collection]
        ),
        server
    )
    port = random.randint(9000, 9999)  # FIXME: This is a hack more than anything else
    server.add_insecure_port(f'0.0.0.0:{port}')
    server.start()

    yield CatalogStub(grpc.insecure_channel(f'0.0.0.0:{port}'))

    server.stop(0)
    client['catalog-test'].drop_collection(parts_collection)
    client['catalog-test'].drop_collection(schemas_collection)


@pytest.fixture
def schema(service):
    schema = PartSchema(
        display_name='Resistor',
        attributes=[
            PartAttributeSchema(
                attribute='resistance',
                unit='Ohms',
                type=PartAttributeSchema.Type.NUMERIC
            ),
            PartAttributeSchema(
                attribute='footprint',
                type=PartAttributeSchema.Type.STRING
            )
        ]
    )

    result = service.CreatePartSchema(CreatePartSchemaRequest(parent='orgs/main', part_schema=schema))
    schema.name = result.name
    return schema
