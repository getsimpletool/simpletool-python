from setuptools import setup
import re
import os


def get_version():
    # Read version from CHANGELOG.md
    with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        match = re.search(r'\[(\d+\.\d+\.\d+)\]', first_line)
        if match:
            version = match.group(1)
            
            # Update version in __init__.py
            init_path = os.path.join('simpletool', '__init__.py')
            with open(init_path, 'r', encoding='utf-8') as init_file:
                init_content = init_file.read()
            
            # Replace version in the header
            updated_init_content = re.sub(
                r'(version:)\s*',
                r'\1 ' + version,
                init_content
            )
            
            with open(init_path, 'w', encoding='utf-8') as init_file:
                init_file.write(updated_init_content)
            
            return version
    return '0.0.0'  # fallback version if not found


setup(name='simpletool',
      version=get_version(),
      description='simpletool',
      url='https://github.com/nchekwa/simpletool-python/tree/master',
      author='Artur Zdolinski',
      author_email='contact@nchekwa.com',
      license='MIT',
      packages=['simpletool'],
      install_requires=['pydantic>=2.0.0', 'typing-extensions', 'pydantic>=2.10.4'],
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
      ],
      zip_safe=False)
