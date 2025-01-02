from setuptools import setup

setup(name='simpletool',
      version='1.0.0',
      description='simpletool',
      url='https://github.com/nchekwa/simpletool-python/tree/master',
      author='Artur Zdolinski',
      author_email='contact@nchekwa.com',
      license='MIT',
      packages=['simpletool'],
      install_requires=['pydantic>=2.0.0', 'typing-extensions'],
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
      ],
      zip_safe=False)
