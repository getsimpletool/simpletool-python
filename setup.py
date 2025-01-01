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
      zip_safe=False)
