
import grpc

from avninv.catalog.v1.catalog_pb2 import CreatePartRequest, DeletePartRequest, GetPartRequest, PartAttribute, Part, PartSupplier


def test_CreatePart(service):
    p1 = Part(
        manufacturer_part_number='mfg_01',
        type='resistance',
        description='RES 10K 0502',
        attributes=[
            PartAttribute(
                attribute='Resistance',
                unit='Ohms',
                numeric_value=10e3,
                value='10k'
            )
        ],
        suppliers=[
            PartSupplier(
                supplier='digikey',
                supplier_part_number='DIG0001',
                url='https://digikey.ca/wee'
            )
        ]
    )

    result = service.CreatePart(CreatePartRequest(parent='org/main/parts', part=p1))
    assert result.name.startswith('org/main/parts/')
    assert len(result.name.split('/')[-1]) == 24


def test_GetPart(service):
    p1 = Part(
        manufacturer_part_number='mfg_01',
        type='resistance',
        description='RES 10K 0502',
        attributes=[
            PartAttribute(
                attribute='Resistance',
                unit='Ohms',
                numeric_value=10e3,
                value='10k'
            )
        ],
        suppliers=[
            PartSupplier(
                supplier='digikey',
                supplier_part_number='DIG0001',
                url='https://digikey.ca/wee'
            )
        ]
    )

    name = service.CreatePart(CreatePartRequest(parent='org/main/parts', part=p1)).name
    p1.name = name

    result = service.GetPart(GetPartRequest(name=name))
    assert result == p1


def test_GetPart_returns_not_found_if_part_doesnt_exist(service):
    try:
        service.GetPart(GetPartRequest(name='org/main/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.NOT_FOUND, error.details()


def test_GetPart_returns_invalid_if_invalid_id(service):
    try:
        service.GetPart(GetPartRequest(name='org/main/parts/notanid'))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()


def test_GetPart_returns_invalid_argument_if_org_invalid(service):
    try:
        service.GetPart(GetPartRequest(name='org/wack/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()


def test_GetPart_returns_invalid_argument_if_path_invalid(service):
    try:
        service.GetPart(GetPartRequest(name='org/wack/main/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()

    try:
        service.GetPart(GetPartRequest(name='org/main/wack/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()


def test_DeletePart(service):
    p1 = Part(
        manufacturer_part_number='mfg_01',
        type='resistance',
        description='RES 10K 0502',
    )

    name = service.CreatePart(CreatePartRequest(parent='org/main/parts', part=p1)).name
    service.GetPart(GetPartRequest(name=name))
    service.DeletePart(DeletePartRequest(name=name))


def test_DeletePart_returns_not_found_if_part_doesnt_exist(service):
    try:
        service.DeletePart(DeletePartRequest(name='org/main/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.NOT_FOUND, error.details()


def test_DeletePart_returns_invalid_if_invalid_id(service):
    try:
        service.DeletePart(DeletePartRequest(name='org/main/parts/notanid'))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()
