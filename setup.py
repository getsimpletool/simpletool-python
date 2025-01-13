from setuptools import setup
import re
import os


def get_version():
    # Read version from CHANGELOG.md
    try:
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Modified pattern to match both # [...] and ## [...]
                match = re.search(r'^#{1,2}\s*\[(\d+\.\d+\.\d+)\]', line)
                if match:
                    version = match.group(1)

                    # Update version in __init__.py
                    init_path = os.path.join('simpletool', '__init__.py')
                    try:
                        with open(init_path, 'r', encoding='utf-8') as init_file:
                            init_content = init_file.read()

                        # Replace version in the header
                        updated_init_content = re.sub(
                            r'version:\s*\d+\.\d+\.\d+',
                            f'version: {version}',
                            init_content
                        )

                        with open(init_path, 'w', encoding='utf-8') as init_file:
                            init_file.write(updated_init_content)

                    except Exception as e:
                        print(f"Error updating __init__.py: {e}")

                    print(f"Found version: {version}")
                    return version
        print("No version found in CHANGELOG.md")
        return '0.0.0'  # fallback version if not found
    except FileNotFoundError:
        print("CHANGELOG.md not found!")
        return '0.0.0'


def read_version_from_init():
    """Read version from __init__.py as a fallback"""
    try:
        init_path = os.path.join('simpletool', '__init__.py')
        with open(init_path, 'r', encoding='utf-8') as init_file:
            init_content = init_file.read()
            match = re.search(r'version:\s*(\d+\.\d+\.\d+)', init_content)
            if match:
                version = match.group(1)
                print(f"Version from __init__.py: {version}")
                return version
    except Exception as e:
        print(f"Error reading version from __init__.py: {e}")
    return '0.0.0'


def write_version_to_metadata(version):
    """Write version to PKG-INFO metadata file"""
    try:
        with open('simpletool.egg-info/PKG-INFO', 'r') as f:
            content = f.read()

        # Replace or add Version
        if 'Version:' in content:
            content = re.sub(r'Version:.*', f'Version: {version}', content)
        else:
            content += f'\nVersion: {version}\n'

        with open('simpletool.egg-info/PKG-INFO', 'w') as f:
            f.write(content)

        print(f"Updated PKG-INFO with version: {version}")
    except Exception as e:
        print(f"Error writing version to metadata: {e}")


# First try to get version from CHANGELOG.md
version = get_version()

# If that fails, try reading from __init__.py
if version == '0.0.0':
    version = read_version_from_init()

# Write version to metadata
write_version_to_metadata(version)

setup(name='simpletool',
      version=version,  # Use the version we found
      description='simpletool',
      url='https://github.com/nchekwa/simpletool-python/tree/master',
      author='Artur Zdolinski',
      author_email='contact@nchekwa.com',
      license='MIT',
      packages=['simpletool'],
      install_requires=['pydantic>=2.10.4', 'typing-extensions'],
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      package_data={
          'simpletool': ['CHANGELOG.md', 'LICENSE'],
      },
      include_package_data=True,
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
      ],
      zip_safe=False)
