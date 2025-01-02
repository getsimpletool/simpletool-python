from setuptools import setup

setup(name='simpletool',
      version='0.0.2',
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
