import concurrent.futures
import uuid
import os

import grpc
import pymongo
import pytest
import yaml

from avninv.catalog.catalog import CatalogService

from avninv.catalog.v1.catalog_pb2_grpc import add_CatalogServicer_to_server, CatalogStub


class ConfigNotFoundException(Exception):
    pass


def _get_config():
    paths = ['config.test.yaml', 'config.test.ci.yaml']
    for path in paths:
        if os.path.isfile(path):
            return open(path, 'r')
    raise ConfigNotFoundException


@pytest.fixture
def service():
    config = yaml.load(_get_config(), Loader=yaml.CLoader)
    client = pymongo.MongoClient(config['database'][0], serverSelectionTimeoutMS=1000)
    collection = str(uuid.uuid4())

    client['catalog-test'].create_collection(collection)

    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=1))
    add_CatalogServicer_to_server(CatalogService(client['catalog-test'][collection]), server)
    server.add_insecure_port('0.0.0.0:9321')

    server.start()
    yield CatalogStub(grpc.insecure_channel('0.0.0.0:9321'))
    server.stop(0)
    client['catalog-test'].drop_collection(collection)
