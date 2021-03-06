import pytest
from jsonschema import ValidationError

from jsonrpcclient import exceptions
from jsonrpcclient.parse import JSONRPCResponse, parse


class TestJSONRPCResponse:
    """
    A single success response.
    """

    def test(self, *_):
        response = JSONRPCResponse({"jsonrpc": "2.0", "result": 5, "id": 1})
        assert response.ok == True
        assert response.id == 1
        assert response.result == 5
        assert repr(response) == "<JSONRPCResponse(id=1, result=5)>"

    def test_null_id(self, *_):
        response = JSONRPCResponse({"jsonrpc": "2.0", "result": 5, "id": None})
        # Acceptable.
        assert response.ok == True
        assert response.id == None

    def test_none(self, *_):
        response = JSONRPCResponse(None)
        # Is an acceptable response.
        assert response.ok == True
        assert response.id == None
        assert response.result == None

    def test_empty_string(self):
        response = JSONRPCResponse("")
        # Also acceptable (response to notification requests).
        assert response.ok == True
        assert response.result == None

    def test_error(self, *_):
        received = {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Not Found"},
            "id": 1,
        }
        response = JSONRPCResponse(received)
        assert response.ok == False
        assert response.id == 1
        assert response.code == -32000
        assert response.message == "Not Found"
        assert repr(response) == '<JSONRPCResponse(id=1, message="Not Found")>'

    def test_error_with_data(self, *_):
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": "Not Found",
                "data": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            },
            "id": None,
        }
        response = JSONRPCResponse(response)
        assert response.code == -32000
        assert response.message == "Not Found"
        assert (
            response.data == "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        )

    def test_error_with_nonstring_data(self, *_):
        """Reported in issue #56"""
        response = {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Not Found", "data": {}},
            "id": None,
        }
        response = JSONRPCResponse(response)
        assert response.code == -32000
        assert response.message == "Not Found"
        assert response.data == {}


class TestParse:
    """
    Could not parse the response.

    Should raise an exception, unless validate_against_schema is False.
    """

    def test(self, *_):
        parse('{"jsonrpc": "2.0", "result": "foo", "id": 1}')

    def test_invalid_json(self, *_):
        with pytest.raises(exceptions.ParseResponseError):
            parse("{dodgy}")

    def test_invalid_jsonrpc(self, *_):
        with pytest.raises(ValidationError):
            parse('{"json": "2.0"}')

    def test_without_validation(self, *_):
        parse(
            '{"jsonrpc": "2.0", "result": "foo", "id": 1}',
            validate_against_schema=False,
        )

    def test_batch(self, *_):
        data = parse('[{"jsonrpc": "2.0", "result": "foo", "id": 1}]')
        assert data[0].result == "foo"

    def test_batch_ignores_notifications(self, *_):
        data = parse('[{"jsonrpc": "2.0", "result": "foo", "id": 1}]')
        assert len(data) == 1

    def test_empty_string(self, *_):
        assert parse("") is None

    def test_none(self, *_):
        assert parse(None) is None

    def test_empty_string(self, *_):
        assert parse("") is None
