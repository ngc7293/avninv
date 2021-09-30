"""Entry point for Catalog service"""

import concurrent.futures

import grpc
import pymongo
import yaml

from avninv.catalog.catalog import CatalogService
from avninv.catalog.catalog_pb2_grpc import add_CatalogServicer_to_server


def make_mongo_uri(config):
    return f"mongodb+srv://{config['user']}:{config['password']}@{config['host']}/{config['database']}?retryWrites=true&w=majority"


def main(args):
    config = yaml.load(open('config.local.yaml', 'r'), Loader=yaml.CLoader)

    client = pymongo.MongoClient(make_mongo_uri(config['database']))
    service = CatalogService(client['catalog']['parts'])
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))

    add_CatalogServicer_to_server(service, server)
    for address in config['server']['addresses']:
        server.add_insecure_port(address)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    exit(main(None) or 0)