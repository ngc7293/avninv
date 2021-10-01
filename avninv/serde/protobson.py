"""Protobuf-to-BSON and BSON-to-Protobuf serde"""

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.reflection import MakeClass


def _get_id_field_number(descriptor):
    for field in descriptor.fields:
        if field.name == 'id' and field.type == FieldDescriptor.TYPE_STRING:
            return field.number
    return None


def protobuf_to_bson(message, map_id=True):
    bson = {}

    for field in message.ListFields():
        if field[0].label == FieldDescriptor.LABEL_REPEATED:
            repeated = []
            for subfield in field[1]:
                if field[0].message_type is not None:
                    repeated.append(protobuf_to_bson(subfield))
                else:
                    repeated.append(subfield)
            bson[str(field[0].number)] = repeated
        elif field[0].message_type is not None:
            bson[str(field[0].number)] = protobuf_to_bson(field[1])
        else:
            bson[str(field[0].number)] = field[1]

    return bson


def bson_to_protobuf(bson, cls=None, descriptor=None, map_id=True):
    cls = cls or MakeClass(descriptor)
    message = cls()
    fields = {field.number: field for field in cls.DESCRIPTOR.fields}

    id_field = _get_id_field_number(cls.DESCRIPTOR)

    for key in bson:
        if key == '_id':
            setattr(message, fields[id_field].name, str(bson[key]))

        if not key.isdigit() or int(key) not in fields:
            continue

        number = int(key)
        if isinstance(bson[key], list):
            repeated = getattr(message, fields[number].name)
            for subfield in bson[key]:
                if isinstance(bson[key][0], dict) and fields[number].message_type is not None:
                    repeated.add().CopyFrom(bson_to_protobuf(subfield, descriptor=fields[number].message_type))
                else:
                    repeated.append(subfield)
        elif isinstance(bson[key], dict):
            if fields[number].message_type is not None:
                nested = bson_to_protobuf(bson[key], descriptor=fields[number].message_type)
                getattr(message, fields[number].name).CopyFrom(nested)
        else:
            setattr(message, fields[number].name, bson[key])

    return message
