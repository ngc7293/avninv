"""Protobuf-to-BSON and BSON-to-Protobuf serde"""

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.reflection import MakeClass


def _get_id_field_number(descriptor):
    for field in descriptor.fields:
        if field.name == 'id' and field.type == FieldDescriptor.TYPE_STRING:
            return field.number
    return None


def _check_if_field_in_mask(field_name, fields_mask):
    if not fields_mask:
        return True
    for field_mask in fields_mask:
        if field_name == field_mask or field_mask.startswith(field_name + '.'):
            return True
    return False


def _check_if_index_in_mask(field_name, field_index, fields_mask):
    if not fields_mask:
        return True
    for field_mask in fields_mask:
        if field_mask.startswith(f'{field_name}.{field_index}'):
            return True
    return False


def _subfield_mask(subfield_name, fields_mask, strip_first=False):
    if not fields_mask:
        return None
    offset = 1 if not strip_first else 2
    return [m.split('.', offset)[offset] for m in fields_mask if m.startswith(subfield_name + '.')]


def protobuf_to_bson(message, fields_mask=None, preserve_index=False):
    bson = {}

    for descriptor, value in message.ListFields():
        field_id = f'_{descriptor.number}'

        if not _check_if_field_in_mask(descriptor.name, fields_mask):
            continue

        if descriptor.label == FieldDescriptor.LABEL_REPEATED:
            repeated = []
            for index, subfield in enumerate(value):
                if _check_if_index_in_mask(descriptor.name, index, fields_mask):
                    if descriptor.message_type is not None:
                        repeated.append(protobuf_to_bson(subfield, fields_mask=_subfield_mask(descriptor.name, fields_mask, True)))
                    else:
                        repeated.append(subfield)
                elif preserve_index:
                    repeated.append(None)
            bson[field_id] = repeated
        elif descriptor.message_type is not None:
            bson[field_id] = protobuf_to_bson(value, fields_mask=_subfield_mask(descriptor.name, fields_mask))
        else:
            bson[field_id] = value

    return bson


def bson_to_protobuf(bson, cls=None, descriptor=None):
    cls = cls or MakeClass(descriptor)
    message = cls()
    fields = {field.number: field for field in cls.DESCRIPTOR.fields}

    id_field = _get_id_field_number(cls.DESCRIPTOR)

    for key in bson:
        if key == '_id':
            if id_field is not None:
                setattr(message, fields[id_field].name, str(bson[key]))
            continue

        if not key[0] == '_' and not key[1:].isdigit() or int(key[1:]) not in fields:
            # uh-oh
            continue

        number = int(key[1:])
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


def _flatten(bson):
    for key in bson.keys():
        if isinstance(bson[key], dict):
            for subkey, value in _flatten(bson[key]):
                yield (f'{key}.{subkey}', value)
        elif isinstance(bson[key], list):
            for index, value in enumerate(bson[key]):
                if value:
                    if isinstance(value, dict):
                        for subkey, subvalue in _flatten(value):
                            yield (f'{key}.{index}.{subkey}', subvalue)
                    else:
                        yield (f'{key}.{index}', value)
        else:
            yield (key, bson[key])


def _get_field_descriptor_by_name(message_descriptor, name):
    for descriptor in message_descriptor.fields:
        if descriptor.name == name:
            return descriptor

def _proto_mask_to_bson_mask(message_descriptor, fields_mask):
    for field in fields_mask:
        tokens = field.split('.')
        descriptor = _get_field_descriptor_by_name(message_descriptor, tokens[0])

        if not descriptor:
            continue

        field_id = f'_{descriptor.number}'

        if descriptor.label == FieldDescriptor.LABEL_REPEATED:
            if len(tokens) < 2 or not tokens[1].isdigit():
                continue

            if descriptor.message_type != None and len(tokens) > 2:
                for path, indexed in _proto_mask_to_bson_mask(descriptor.message_type, _subfield_mask(tokens[0], fields_mask, True)):
                    yield (f'{field_id}.{tokens[1]}.{path}', indexed)
            else:
                yield (f'{field_id}.{tokens[1]}', True)

        elif descriptor.message_type != None:
            if len(tokens) == 1:
                yield (f'{field_id}', False)
            else:
                for path, indexed in _proto_mask_to_bson_mask(descriptor.message_type, _subfield_mask(tokens[0], fields_mask)):
                    yield (f'{field_id}.{path}', indexed)
        else:
            if len(tokens) == 1:
                yield (f'{field_id}', False)


def protobuf_to_update_document(message, fields_mask):
    bson = protobuf_to_bson(message, fields_mask=fields_mask, preserve_index=True)
    flatbson = {f: k for f, k in _flatten(bson)}
    fields_id_mask = list(_proto_mask_to_bson_mask(message.DESCRIPTOR, fields_mask))

    return {
        '$set': flatbson,
        '$unset': {path: '' for path, _ in fields_id_mask if path not in flatbson},
        '$pull':  {path.rsplit('.', 1)[0]: None for path, indexed in fields_id_mask if path not in flatbson and indexed}
    }