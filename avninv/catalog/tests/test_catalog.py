
import grpc
from grpc_status import rpc_status

from avninv.catalog.proto.catalog_pb2 import AddPartRequest, GetPartRequest, PartAttributes, PartDetails, PartSupplier


def test_AddPart(service):
    p1 = PartDetails(
        manufacturer_part_number='mfg_01',
        type='resistance',
        description='RES 10K 0502',
        attributes=[
            PartAttributes(
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

    result = service.AddPart(AddPartRequest(details=p1))
    assert result.id != ''


def test_GetPart(service):
    p1 = PartDetails(
        manufacturer_part_number='mfg_01',
        type='resistance',
        description='RES 10K 0502',
        attributes=[
            PartAttributes(
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

    id = service.AddPart(AddPartRequest(details=p1)).id
    result = service.GetPart(GetPartRequest(id=id))

    assert result.details == p1


def test_GetPart_returns_not_found_if_invalid_id(service):
    try:
        service.GetPart(GetPartRequest(id='0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.NOT_FOUND, error.details()
