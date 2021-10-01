"""Entry point for Catalog service"""


import argparse
import concurrent.futures
import signal
import os

import grpc
import pymongo
import yaml

from avninv.catalog.catalog import CatalogService
from avninv.catalog.proto.catalog_pb2_grpc import add_CatalogServicer_to_server


def main(args):
    if not os.path.exists(args.config):
        print(f'Could not find file {args.config}')
        return -1

    config = yaml.load(open(args.config, 'r'), Loader=yaml.CLoader)

    client = pymongo.MongoClient(config['database'][0])
    service = CatalogService(client['catalog']['parts'])

    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    add_CatalogServicer_to_server(service, server)

    for address in config['server']['addresses']:
        server.add_insecure_port(address)

    server.start()
    signal.signal(signal.SIGINT, lambda *_: server.stop(0.5))

    print(f'Listening on [{", ".join(config["server"]["addresses"])}]')
    server.wait_for_termination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    exit(main(parser.parse_args()) or 0)
