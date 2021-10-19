
from google.protobuf.field_mask_pb2 import FieldMask
import grpc
import pytest

from avninv.catalog.catalog import CatalogService
from avninv.catalog.v1.catalog_pb2 import CreatePartRequest, DeletePartRequest, GetPartRequest, PartAttribute, Part, PartSupplier, UpdatePartRequest
from avninv.error.api_error import ApiError

@pytest.mark.parametrize("path,valid", [
    ('org/main/parts/wee', False),
    ('org/main/parts',     False),
    ('orgs/other/parts',   False),
    ('orgs/main/part',     False),
    ('orgs/main/parts',    True)
])
def test_validate_parent(path, valid):
    if not valid:
        with pytest.raises(ApiError):
            CatalogService._validate_parent(path, 'main')
    else:
        assert CatalogService._validate_parent(path, 'main') == 'main'

@pytest.mark.parametrize("path,valid", [
    ('org/main/parts',       False),
    ('org/main/parts/wee',   False),
    ('orgs/other/parts/wee', False),
    ('orgs/main/part/wee',   False),
    ('orgs/main/parts/wee',  True)
])
def test_validate_name(path, valid):
    if not valid:
        with pytest.raises(ApiError):
            CatalogService._validate_name(path, 'main')
    else:
        assert CatalogService._validate_name(path, 'main') == ('main', 'wee')

def test_CreatePart(service):
    p1 = Part(
        manufacturer_part_number='mfg_01',
        schema_name='resistance',
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

    result = service.CreatePart(CreatePartRequest(parent='orgs/main/parts', part=p1))
    assert result.name.startswith('orgs/main/parts/')
    assert len(result.name.split('/')[-1]) == 24


def test_GetPart(service):
    p1 = Part(
        manufacturer_part_number='mfg_01',
        schema_name='resistance',
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

    name = service.CreatePart(CreatePartRequest(parent='orgs/main/parts', part=p1)).name
    p1.name = name

    result = service.GetPart(GetPartRequest(name=name))
    assert result == p1


def test_GetPart_returns_not_found_if_part_doesnt_exist(service):
    try:
        service.GetPart(GetPartRequest(name='orgs/main/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.NOT_FOUND, error.details()


def test_GetPart_returns_invalid_if_invalid_id(service):
    try:
        service.GetPart(GetPartRequest(name='orgs/main/parts/notanid'))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()


def test_GetPart_returns_invalid_argument_if_org_invalid(service):
    try:
        service.GetPart(GetPartRequest(name='orgs/wack/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()


def test_GetPart_returns_invalid_argument_if_path_invalid(service):
    try:
        service.GetPart(GetPartRequest(name='orgs/wack/main/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()

    try:
        service.GetPart(GetPartRequest(name='org/smain/wack/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()


def test_DeletePart(service):
    p1 = Part(
        manufacturer_part_number='mfg_01',
        schema_name='resistance',
        description='RES 10K 0502',
    )

    name = service.CreatePart(CreatePartRequest(parent='orgs/main/parts', part=p1)).name
    service.GetPart(GetPartRequest(name=name))
    service.DeletePart(DeletePartRequest(name=name))


def test_DeletePart_returns_not_found_if_part_doesnt_exist(service):
    try:
        service.DeletePart(DeletePartRequest(name='orgs/main/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.NOT_FOUND, error.details()


def test_DeletePart_returns_invalid_if_invalid_id(service):
    try:
        service.DeletePart(DeletePartRequest(name='orgs/main/parts/notanid'))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.INVALID_ARGUMENT, error.details()


def test_UpdatePart(service):
    p1 = Part(
        manufacturer_part_number='mfg_01',
        schema_name='resistance',
        description='RES 10K 0502',
        attributes=[
            PartAttribute(
                attribute='Resistance',
                unit='Ohms',
                numeric_value=10e3,
                value='10k'
            ),
            PartAttribute(
                attribute='Footprint',
                value='0502'
            )
        ],
        suppliers=[
            PartSupplier(
                supplier='digikey',
                supplier_part_number='DIG0001',
                url='https://digikey.ca/wee'
            ),
            PartSupplier(
                supplier='mouser',
                supplier_part_number='MOUS0001',
                url='https://mouser.ca/woo'
            )
        ]
    )

    name = service.CreatePart(CreatePartRequest(parent='orgs/main/parts', part=p1)).name
    
    p2 = Part(
        description='RES 10K 0203',
        attributes=[
            PartAttribute(),
            PartAttribute(
                value='0203'
            )
        ]
    )
    masks = [
        'description',
        'attributes.1.value',
        'suppliers.0'
    ]

    service.UpdatePart(UpdatePartRequest(name=name, part=p2, update_mask=FieldMask(paths=masks)))
    result = service.GetPart(GetPartRequest(name=name))
    result.name = ''

    assert result == Part(
        manufacturer_part_number='mfg_01',
        schema_name='resistance',
        description='RES 10K 0203',
        attributes=[
            PartAttribute(
                attribute='Resistance',
                unit='Ohms',
                numeric_value=10e3,
                value='10k'
            ),
            PartAttribute(
                attribute='Footprint',
                value='0203'
            )
        ],
        suppliers=[
            PartSupplier(
                supplier='mouser',
                supplier_part_number='MOUS0001',
                url='https://mouser.ca/woo'
            )
        ]
    )