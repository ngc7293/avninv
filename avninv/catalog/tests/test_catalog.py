
from google.protobuf.field_mask_pb2 import FieldMask
import grpc
import pytest

from avninv.catalog.catalog import CatalogService
from avninv.catalog.v1.catalog_pb2 import (
    _PARTATTRIBUTESCHEMA_TYPE, CreatePartRequest, CreatePartSchemaRequest, DeletePartRequest, DeletePartSchemaRequest, GetPartRequest, GetPartSchemaRequest, ListPartRequest, PartAttribute, Part, PartAttributeSchema, PartSchema, PartSupplier, UpdatePartRequest
)
from avninv.error.api_error import ApiError


@pytest.mark.parametrize("path,valid", [
    ('org/main/parts/wee', False),
    ('org/main/parts', False),
    ('orgs/other/parts', False),
    ('orgs/main/part', False),
    ('orgs/main/parts', True)
])
def test_validate_parent(path, valid):
    if not valid:
        with pytest.raises(ApiError):
            CatalogService._validate_parent(path, 'parts', 'main')
    else:
        assert CatalogService._validate_parent(path, 'parts', 'main') == 'main'


@pytest.mark.parametrize("path,valid", [
    ('org/main/parts', False),
    ('org/main/parts/wee', False),
    ('orgs/other/parts/wee', False),
    ('orgs/main/part/wee', False),
    ('orgs/main/parts/wee', True)
])
def test_validate_name(path, valid):
    if not valid:
        with pytest.raises(ApiError):
            CatalogService._validate_name(path, 'parts', 'main')
    else:
        assert CatalogService._validate_name(path, 'parts', 'main') == ('main', 'wee')


class TestParts:
    def test_CreatePart(self, service, schema):
        p1 = Part(
            manufacturer_part_number='mfg_01',
            schema_name=schema.name,
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

    def test_CreatePart_fails_if_no_such_schema(self, service):
        p1 = Part(
            manufacturer_part_number='mfg_01',
            description='This is a description',
            schema_name='orgs/main/partschemas/' + '0' * 24,
        )

        with pytest.raises(grpc.RpcError) as error:
            service.CreatePart(CreatePartRequest(parent='orgs/main/parts', part=p1))
        assert error.value.code() == grpc.StatusCode.NOT_FOUND, error.value.details()

    def test_GetPart(self, service, schema):
        p1 = Part(
            manufacturer_part_number='mfg_01',
            schema_name=schema.name,
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

    def test_GetPart_returns_not_found_if_part_doesnt_exist(self, service):
        with pytest.raises(grpc.RpcError) as error:
            service.GetPart(GetPartRequest(name='orgs/main/parts/' + '0' * 24))
        assert error.value.code() == grpc.StatusCode.NOT_FOUND, error.value.details()

    def test_GetPart_returns_invalid_if_invalid_id(self, service):
        with pytest.raises(grpc.RpcError) as error:
            service.GetPart(GetPartRequest(name='orgs/main/parts/notanid'))
        assert error.value.code() == grpc.StatusCode.INVALID_ARGUMENT, error.value.details()

    def test_GetPart_returns_invalid_argument_if_org_invalid(self, service):
        with pytest.raises(grpc.RpcError) as error:
            service.GetPart(GetPartRequest(name='orgs/wack/parts/' + '0' * 24))
        assert error.value.code() == grpc.StatusCode.INVALID_ARGUMENT, error.value.details()

    def test_GetPart_returns_invalid_argument_if_path_invalid(self, service):
        with pytest.raises(grpc.RpcError) as error:
            service.GetPart(GetPartRequest(name='orgs/wack/main/parts/' + '0' * 24))
        assert error.value.code() == grpc.StatusCode.INVALID_ARGUMENT, error.value.details()

        with pytest.raises(grpc.RpcError) as error:
            service.GetPart(GetPartRequest(name='org/smain/wack/' + '0' * 24))
        assert error.value.code() == grpc.StatusCode.INVALID_ARGUMENT, error.value.details()

    def test_DeletePart(self, service, schema):
        p1 = Part(
            manufacturer_part_number='mfg_01',
            schema_name=schema.name,
            description='RES 10K 0502',
        )

        name = service.CreatePart(CreatePartRequest(parent='orgs/main/parts', part=p1)).name
        service.DeletePart(DeletePartRequest(name=name))

        with pytest.raises(grpc.RpcError) as error:
            service.GetPart(GetPartRequest(name=name))
        assert error.value.code() == grpc.StatusCode.NOT_FOUND, error.value.details()

    def test_DeletePart_returns_not_found_if_part_doesnt_exist(self, service):
        with pytest.raises(grpc.RpcError) as error:
            service.DeletePart(DeletePartRequest(name='orgs/main/parts/' + '0' * 24))
        assert error.value.code() == grpc.StatusCode.NOT_FOUND, error.value.details()

    def test_DeletePart_returns_invalid_if_invalid_id(self, service):
        with pytest.raises(grpc.RpcError) as error:
            service.DeletePart(DeletePartRequest(name='orgs/main/parts/notanid'))
        assert error.value.code() == grpc.StatusCode.INVALID_ARGUMENT, error.value.details()

    def test_UpdatePart(self, service, schema):
        p1 = Part(
            manufacturer_part_number='mfg_01',
            schema_name=schema.name,
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
            schema_name=schema.name,
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

    def test_UpdatePart_fails_if_part_does_not_exist(self, service):
        p1 = Part(
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

        with pytest.raises(grpc.RpcError) as error:
            service.UpdatePart(UpdatePartRequest(
                name='orgs/main/parts/' + '0' * 24,
                part=p1,
                update_mask=FieldMask(paths=masks)
            ))
        assert error.value.code() == grpc.StatusCode.NOT_FOUND, error.value.details()

    def test_ListParts(self, service, schema):
        p1 = Part(
            schema_name=schema.name,
            description='RES 10K 0203',
        )

        names = []
        names.append(service.CreatePart(CreatePartRequest(parent='orgs/main/parts', part=p1)).name)
        names.append(service.CreatePart(CreatePartRequest(parent='orgs/main/parts', part=p1)).name)

        response = service.ListParts(ListPartRequest(parent='orgs/main/parts'))
        assert names == [part.name for part in response.parts]


class TestPartSchema:
    def test_CreatePartSchema(self, service):
        m1 = PartSchema(
            name='fizzbuzz',
            display_name='Resistor',
            attributes=[
                PartAttributeSchema(
                    attribute='resistance',
                    unit='Ohms',
                    type=PartAttributeSchema.Type.NUMERIC
                )
            ]
        )

        result = service.CreatePartSchema(CreatePartSchemaRequest(parent='orgs/main/partschemas', schema=m1))
        assert result.name.startswith('orgs/main/partschemas')
        assert len(result.name.split('/')) == 4

    def test_GetPartSchema(self, service):
        m1 = PartSchema(
            name='fizzbuzz',
            display_name='Resistor',
            attributes=[
                PartAttributeSchema(
                    attribute='resistance',
                    unit='Ohms',
                    type=PartAttributeSchema.Type.NUMERIC
                )
            ]
        )

        result = service.CreatePartSchema(CreatePartSchemaRequest(parent='orgs/main/partschemas', schema=m1))
        m1.name = result.name
        assert service.GetPartSchema(GetPartSchemaRequest(name=result.name)) == m1

    def test_DeletePartSchema(self, service):
        m1 = PartSchema(
            name='fizzbuzz',
            display_name='Resistor'
        )

        result = service.CreatePartSchema(CreatePartSchemaRequest(parent='orgs/main/partschemas', schema=m1))
        service.DeletePartSchema(DeletePartSchemaRequest(name=result.name))

        with pytest.raises(grpc.RpcError) as error:
            service.GetPartSchema(GetPartSchemaRequest(name=result.name))
        assert error.value.code() == grpc.StatusCode.NOT_FOUND, error.value.details()

    def test_ListPartSchema(self, service):
        m1 = PartSchema(
            name='fizzbuzz',
            display_name='Resistor',
            attributes=[
                PartAttributeSchema(
                    attribute='resistance',
                    unit='Ohms',
                    type=PartAttributeSchema.Type.NUMERIC
                )
            ]
        )

        names = []
        names.append(service.CreatePartSchema(CreatePartSchemaRequest(parent='orgs/main/partschemas', schema=m1)).name)
        names.append(service.CreatePartSchema(CreatePartSchemaRequest(parent='orgs/main/partschemas', schema=m1)).name)

        response = service.ListPartSchemas(ListPartRequest(parent='orgs/main/partschemas'))
        assert names == [schema.name for schema in response.schemas]
