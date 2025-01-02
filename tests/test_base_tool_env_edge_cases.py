import os
import pytest
from typing import Dict, Any
from simpletool import BaseTool
from pydantic import BaseModel, Field
from unittest.mock import Mock


class DummyInputModel(BaseModel):
    dummy_field: str = Field(description="A dummy field")


class DummyTool(BaseTool):
    name = "dummy_tool"
    input_schema = DummyInputModel.model_json_schema()

    def __init__(self):
        super().__init__(description="A dummy tool for testing")

    def run(self, arguments: Dict[str, Any]):
        return []


class TestBaseTool:
    def test_get_env_prefix_types(self):
        """Test get_env method with different prefix types."""
        tool = Mock(spec=BaseTool)
        tool.get_env = BaseTool.get_env.__get__(tool)

        os.environ['TEST_VAR1'] = 'value1'
        os.environ['TEST_VAR2'] = 'value2'
        os.environ['OTHER_VAR'] = 'other_value'

        try:
            env_result = tool.get_env({}, prefix='TEST_')
            assert 'TEST_VAR1' in env_result
            assert 'TEST_VAR2' in env_result
            assert 'OTHER_VAR' not in env_result

            env_result = tool.get_env({}, prefix=['TEST_', 'OTHER_'])
            assert 'TEST_VAR1' in env_result
            assert 'TEST_VAR2' in env_result
            assert 'OTHER_VAR' in env_result

            env_result = tool.get_env({}, prefix={'TEST_': 'something', 'OTHER_': 'another'})
            assert 'TEST_VAR1' in env_result
            assert 'TEST_VAR2' in env_result
            assert 'OTHER_VAR' in env_result

        finally:
            del os.environ['TEST_VAR1']
            del os.environ['TEST_VAR2']
            del os.environ['OTHER_VAR']

    def test_get_env_api_key_replacement(self):
        """Test get_env method with API key replacement."""
        tool = Mock(spec=BaseTool)
        tool.get_env = BaseTool.get_env.__get__(tool)
        tool._select_random_api_key = BaseTool._select_random_api_key.__get__(tool)

        os.environ['OPENAI_API_KEYS'] = 'key1,key2,key3'

        try:
            env_result = tool.get_env({}, prefix='OPENAI_')
            assert env_result['OPENAI_API_KEYS'] in ['key1', 'key2', 'key3']

        finally:
            del os.environ['OPENAI_API_KEYS']


class TestBaseToolSubclassValidation:
    def test_empty_name_raises_error(self):
        with pytest.raises(TypeError, match="must define a non-empty 'name' string attribute"):
            type('EmptyNameTool', (BaseTool,), {
                'name': '',
                'input_schema': {"type": "object"},
                'run': lambda self, arguments: []
            })

    def test_non_string_name_raises_error(self):
        with pytest.raises(TypeError, match="must define a non-empty 'name' string attribute"):
            type('NonStringNameTool', (BaseTool,), {
                'name': 123,
                'input_schema': {"type": "object"},
                'run': lambda self, arguments: []
            })

    def test_non_dict_input_schema_raises_error(self):
        with pytest.raises(TypeError, match="must define 'input_schema' as a dictionary"):
            type('NonDictInputSchemaTool', (BaseTool,), {
                'name': 'non_dict_input_schema',
                'input_schema': "not a dictionary",
                'run': lambda self, arguments: []
            })
