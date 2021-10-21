"""Test for the Protobuf-to-BSON serde"""

from google.protobuf.json_format import MessageToDict

from avninv.serde.protobson import (
    bson_to_protobuf, protobuf_to_bson, _flatten, _proto_mask_to_bson_mask, protobuf_to_update_document
)

from avninv.serde.tests.test_protobson_pb2 import _TestMessage, _OtherTestMessage


def test_protobuf_to_bson():
    m1 = _TestMessage(
        string_field_1='alpha',
        uint64_field_2=200,
        message_field_3=_OtherTestMessage(
            sint64_field_1=-1,
            bytes_field_2=b'bytes'
        ),
        repeated_nested_field_4=[
            _TestMessage._NestedTestMessage(
                bool_field_1=True,
                int64_field_2=42
            )
        ],
        repeated_string_field_5=[
            'bravo', 'charlie'
        ]
    )

    assert protobuf_to_bson(m1) == {
        '_1': 'alpha',
        '_2': 200,
        '_3': {'_1': -1, '_2': b'bytes'},
        '_4': [{'_1': True, '_2': 42}],
        '_5': ['bravo', 'charlie']
    }


def test_protobuf_to_bson_handles_missing_and_default_fields():
    m1 = _TestMessage(
        uint64_field_2=0,
        repeated_nested_field_4=[
            _TestMessage._NestedTestMessage(
                bool_field_1=False,
                int64_field_2=42
            )
        ],
        repeated_string_field_5=[
            'bravo', 'charlie'
        ]
    )

    assert protobuf_to_bson(m1) == {
        '_4': [{'_2': 42}],
        '_5': ['bravo', 'charlie']
    }


def test_protobuf_to_bson_handles_field_masks():
    m1 = _TestMessage(
        uint64_field_2=2,
        repeated_nested_field_4=[
            _TestMessage._NestedTestMessage(
                bool_field_1=True,
                int64_field_2=42
            )
        ],
        repeated_string_field_5=[
            'bravo', 'charlie'
        ]
    )

    b1 = protobuf_to_bson(m1, fields_mask=[
        'uint64_field_2', 'repeated_nested_field_4.0.int64_field_2', 'repeated_string_field_5.1'
    ])

    assert b1 == {
        '_2': 2,
        '_4': [{'_2': 42}],
        '_5': ['charlie']
    }


def test_bson_to_protobuf():
    b1 = {
        '_id': '1' * 24,
        '_1': 'alpha',
        '_2': 200,
        '_3': {'_1': -1, '_2': b'bytes'},
        '_4': [{'_1': True, '_2': 42}],
        '_5': ['bravo', 'charlie']
    }

    assert bson_to_protobuf(b1, _TestMessage) == _TestMessage(
        string_field_1='alpha',
        uint64_field_2=200,
        message_field_3=_OtherTestMessage(
            sint64_field_1=-1,
            bytes_field_2=b'bytes'
        ),
        repeated_nested_field_4=[
            _TestMessage._NestedTestMessage(
                bool_field_1=True,
                int64_field_2=42
            )
        ],
        repeated_string_field_5=[
            'bravo', 'charlie'
        ],
        id='1' * 24
    )


def test_bson_to_protobuf_handles_missing_fields():
    b1 = {
        '_4': [{'_2': 42}],
        '_5': ['bravo', 'charlie']
    }
    print(MessageToDict(bson_to_protobuf(b1, _TestMessage)))
    assert bson_to_protobuf(b1, _TestMessage) == _TestMessage(
        uint64_field_2=0,
        repeated_nested_field_4=[
            _TestMessage._NestedTestMessage(
                bool_field_1=False,
                int64_field_2=42
            )
        ],
        repeated_string_field_5=[
            'bravo', 'charlie'
        ]
    )


def test_bson_to_protobuf_handles_empty_message():
    assert bson_to_protobuf({}, _TestMessage) == _TestMessage()


def test__flatten_bson():
    bson = {
        '_4': [{'_2': 42}],
        '_5': ['bravo', 'charlie']
    }

    assert list(_flatten(bson)) == [
        ('_4.0._2', 42),
        ('_5.0', 'bravo'),
        ('_5.1', 'charlie')
    ]


def test_fields_mask_to_field_id():
    fields_mask = [
        'string_field_1',
        'uint64_field_2',
        'repeated_nested_field_4.2.bool_field_1'
    ]

    assert list(_proto_mask_to_bson_mask(_TestMessage.DESCRIPTOR, fields_mask)) == [
        ('_1', False),
        ('_2', False),
        ('_4.2._1', False)
    ]


def test_protobuf_to_update_document():
    m1 = _TestMessage(
        string_field_1='alpha',
        uint64_field_2=200,
        repeated_nested_field_4=[
            _TestMessage._NestedTestMessage(
                bool_field_1=True,
                int64_field_2=42
            )
        ],
        repeated_string_field_5=[
            'bravo', 'charlie'
        ]
    )

    fm = [
        'string_field_1',
        'uint64_field_2',
        'message_field_3',
        'repeated_nested_field_4.0.bool_field_1',
        'repeated_string_field_5.2'
    ]

    assert protobuf_to_update_document(m1, fm) == {
        '$set': {
            '_1': 'alpha',
            '_2': 200,
            '_4.0._1': True
        },
        '$unset': {'_3': '', '_5.2': ''},
        '$pull': {'_5': None}
    }
