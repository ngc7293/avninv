from grpc_status.rpc_status import to_status
from google.rpc.status_pb2 import Status
from google.rpc.code_pb2 import Code

StatusCode = Code


def rpc_status(code, message=''):
    return to_status(Status(code=code, message=message))
