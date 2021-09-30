"""Protobuf-to-BSON and BSON-to-Protobuf serde"""

from google.protobuf.descriptor import FieldDescriptor


def protobuf_to_bson(message):
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


def bson_to_protobuf(bson, cls):
    message = cls()
    fields = {field.number: field for field in cls.DESCRIPTOR.fields}

    for id in bson:
        if not id.isdigit() or int(id) not in fields:
            continue

        if isinstance(bson[id], list):
            repeated = getattr(message, fields[int(id)].name)
            for subfield in bson[id]:
                if isinstance(bson[id][0], dict) and fields[int(id)].message_type is not None:
                    repeated.add().CopyFrom(bson_to_protobuf(subfield, getattr(cls, fields[int(id)].message_type.name)))
                else:
                    repeated.append(subfield)
        elif isinstance(bson[id], dict):
            if fields[int(id)].message_type is not None:
                nested = bson_to_protobuf(bson[id], getattr(cls, fields[int(id)].message_type.name))
                getattr(message, fields[int(id)].name).CopyFrom(nested)
        else:
            setattr(message, fields[int(id)].name, bson[id])

    return message
