from grpc import StatusCode  # noqa


class ApiError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message

    def __str__(self):
        return f'{self.status} ({self.message})'
