
import grpc

from avninv.catalog.v1.catalog_pb2 import CreatePartRequest, GetPartRequest, PartAttribute, Part, PartSupplier


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

    result = service.CreatePart(CreatePartRequest(part=p1))
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

    name = service.CreatePart(CreatePartRequest(part=p1)).name
    p1.name = name

    result = service.GetPart(GetPartRequest(name=name))
    assert result == p1


def test_GetPart_returns_not_found_if_invalid_id(service):
    try:
        service.GetPart(GetPartRequest(name='org/main/parts/' + '0' * 24))
        assert False, 'Should have hit exception!'
    except grpc.RpcError as error:
        assert error.code() == grpc.StatusCode.NOT_FOUND, error.details()
