"""Test for the Protobuf-to-BSON serde"""

from google.protobuf.json_format import MessageToDict

from avninv.serde.protobson import bson_to_protobuf, protobuf_to_bson

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
        '1': 'alpha',
        '2': 200,
        '3': {'1': -1, '2': b'bytes'},
        '4': [{'1': True, '2': 42}],
        '5': ['bravo', 'charlie']
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
        '4': [{'2': 42}],
        '5': ['bravo', 'charlie']
    }


def test_bson_to_protobuf():
    b1 = {
        '1': 'alpha',
        '2': 200,
        '3': {'1': -1, '2': b'bytes'},
        '4': [{'1': True, '2': 42}],
        '5': ['bravo', 'charlie']
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
        ]
    )


def test_bson_to_protobuf_handles_missing_fields():
    b1 = {
        '4': [{'2': 42}],
        '5': ['bravo', 'charlie']
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
