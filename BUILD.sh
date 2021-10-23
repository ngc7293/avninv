#!/bin/bash
python -m grpc_tools.protoc --proto_path=. --python_out=. avninv/serde/tests/test_protobson.proto
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. avninv/catalog/v1/catalog.proto
python -m grpc_tools.protoc --proto_path=. --include_imports --include_source_info --descriptor_set_out=avninv/catalog/v1/catalog.pb avninv/catalog/v1/catalog.proto