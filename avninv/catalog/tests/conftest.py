import concurrent.futures
import uuid

import grpc
import pymongo
import pytest
import yaml

from avninv.catalog.catalog import CatalogService

from avninv.catalog.proto.catalog_pb2_grpc import add_CatalogServicer_to_server, CatalogStub


def make_mongo_uri(config):
    return f"mongodb+srv://{config['user']}:{config['password']}@{config['host']}/{config['database']}?retryWrites=true&w=majority"


@pytest.fixture
def service():
    config = yaml.load(open('config.test.yaml', 'r'), Loader=yaml.CLoader)
    client = pymongo.MongoClient(make_mongo_uri(config['database']))
    collection = str(uuid.uuid4())

    client['catalog-test'].create_collection(collection)

    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=1))
    add_CatalogServicer_to_server(CatalogService(client['catalog-test'][collection]), server)
    server.add_insecure_port('0.0.0.0:9321')

    server.start()
    yield CatalogStub(grpc.insecure_channel('0.0.0.0:9321'))
    server.stop(0)
    client['catalog-test'].drop_collection(collection)
