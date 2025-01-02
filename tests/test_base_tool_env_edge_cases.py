import os
import pytest
from simpletool import BaseTool
from typing import Dict, Any
from pydantic import BaseModel, Field
from unittest.mock import Mock

class DummyInputModel(BaseModel):
    dummy_field: str = Field(description="A dummy field")

class DummyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="dummy_tool", 
            description="A dummy tool for testing", 
            input_schema=DummyInputModel
        )
    
    def run(self, arguments: Dict[str, Any]):
        return []

class TestBaseTool:
    def test_get_env_prefix_types(self):
        """Test get_env method with different prefix types."""
        # Create a mock BaseTool instance
        tool = Mock(spec=BaseTool)
        tool.get_env = BaseTool.get_env.__get__(tool)
        
        # Set up test environment variables
        os.environ['TEST_VAR1'] = 'value1'
        os.environ['TEST_VAR2'] = 'value2'
        os.environ['OTHER_VAR'] = 'other_value'
        
        try:
            # Test with string prefix
            env_result = tool.get_env({}, prefix='TEST_')
            assert 'TEST_VAR1' in env_result
            assert 'TEST_VAR2' in env_result
            assert 'OTHER_VAR' not in env_result
            
            # Test with list prefix
            env_result = tool.get_env({}, prefix=['TEST_', 'OTHER_'])
            assert 'TEST_VAR1' in env_result
            assert 'TEST_VAR2' in env_result
            assert 'OTHER_VAR' in env_result
            
            # Test with dict prefix
            env_result = tool.get_env({}, prefix={'TEST_': 'something', 'OTHER_': 'another'})
            assert 'TEST_VAR1' in env_result
            assert 'TEST_VAR2' in env_result
            assert 'OTHER_VAR' in env_result
            
            # Test with None prefix (should return all env vars)
            env_result = tool.get_env({}, prefix=None)
            assert 'TEST_VAR1' in env_result
            assert 'TEST_VAR2' in env_result
            assert 'OTHER_VAR' in env_result
            
        finally:
            # Clean up environment variables
            del os.environ['TEST_VAR1']
            del os.environ['TEST_VAR2']
            del os.environ['OTHER_VAR']
    
    def test_get_env_api_key_replacement(self):
        """Test get_env method with API key replacement."""
        # Create a mock BaseTool instance
        tool = Mock(spec=BaseTool)
        tool.get_env = BaseTool.get_env.__get__(tool)
        tool._select_random_api_key = BaseTool._select_random_api_key.__get__(tool)
        
        # Set up test environment variables with multiple API keys
        os.environ['OPENAI_API_KEYS'] = 'key1,key2,key3'
        
        try:
            # Call get_env and verify API key is selected
            env_result = tool.get_env({}, prefix='OPENAI_')
            assert 'OPENAI_API_KEYS' in env_result
            assert env_result['OPENAI_API_KEYS'] in ['key1', 'key2', 'key3']
            
        finally:
            # Clean up environment variables
            del os.environ['OPENAI_API_KEYS']
