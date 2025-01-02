import importlib
import ast
import pytest
import os
import sys
import importlib.util

def test_setup_metadata():
    """Test the metadata in setup.py."""
    # Temporarily modify sys.argv to avoid coverage argument
    original_argv = sys.argv
    sys.argv = ['setup.py']

    try:
        # Dynamically import setup.py as a module to execute its code
        spec = importlib.util.spec_from_file_location("setup", "setup.py")
        setup_module = importlib.util.module_from_spec(spec)
        sys.modules["setup"] = setup_module

        # Monkey patch setuptools.setup to capture arguments
        captured_setup_args = {}
        def capture_setup(**kwargs):
            captured_setup_args.update(kwargs)
        
        import setuptools
        original_setup = setuptools.setup
        setuptools.setup = capture_setup

        # Re-run the setup to capture arguments
        spec.loader.exec_module(setup_module)

        # Restore original setup function
        setuptools.setup = original_setup

        # Verify captured setup arguments
        assert captured_setup_args['name'] == 'simpletool'
        assert 'version' in captured_setup_args and captured_setup_args['version']
        assert captured_setup_args['description'] == 'simpletool'
        assert captured_setup_args['url'] == 'https://github.com/nchekwa/simpletool-python/tree/master'
        assert captured_setup_args['author'] == 'Artur Zdolinski'
        assert captured_setup_args['author_email'] == 'contact@nchekwa.com'
        assert captured_setup_args['license'] == 'MIT'
        assert captured_setup_args['packages'] == ['simpletool']
        assert 'install_requires' in captured_setup_args and captured_setup_args['install_requires']
        assert captured_setup_args['long_description_content_type'] == 'text/markdown'
        
        # Check classifiers
        classifiers = captured_setup_args['classifiers']
        assert 'License :: OSI Approved :: MIT License' in classifiers
        assert 'Programming Language :: Python :: 3' in classifiers
        assert 'Programming Language :: Python :: 3.7' in classifiers
        assert 'Programming Language :: Python :: 3.8' in classifiers
        assert 'Programming Language :: Python :: 3.9' in classifiers
        assert 'Programming Language :: Python :: 3.10' in classifiers
        assert 'Programming Language :: Python :: 3.11' in classifiers
        assert 'Programming Language :: Python :: 3.12' in classifiers
        
        assert captured_setup_args['zip_safe'] == False
        
        # Check README.md exists and is not empty
        readme_path = 'README.md'
        assert os.path.exists(readme_path), f"README.md file does not exist at {readme_path}"
        with open(readme_path, 'r') as readme_file:
            readme_content = readme_file.read().strip()
            assert readme_content, "README.md file is empty"
            
            # Compare normalized content (remove extra whitespace)
            normalized_readme = ' '.join(readme_content.split())
            normalized_long_desc = ' '.join(captured_setup_args['long_description'].split())
            assert normalized_readme == normalized_long_desc, "README.md content does not match long_description"

    finally:
        # Restore original sys.argv
        sys.argv = original_argv
