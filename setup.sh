#!/bin/bash
python -m grpc_tools.protoc --proto_path=. --python_out=. avninv/serde/tests/test_protobson.proto
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. avninv/catalog/catalog.proto