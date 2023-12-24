import io
import os

from setuptools import find_packages, setup


def get_requirements(filename):
    """Get list of packages from a requirements text file"""
    requirements = []
    with open(filename) as f:
        for requirement in f.read().strip().split('\n'):
            if requirement.startswith('-r '):
                requirements += get_requirements(requirement[3:].strip())
            else:
                requirements.append(requirement)

    return requirements


# extra requirements
extras_require = {
    'pandas': get_requirements('requirements-pandas.txt'),
    'dask': get_requirements('requirements-dask.txt'),
    'spark': get_requirements('requirements-spark.txt')
}
extras_require['all'] = set(sum(extras_require.values(), []))

# use readme file as long description
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup_conf = dict(name='pond',
                  version='0.1.0',
                  description='A library to keep scientists from losing their minds: storage, '
                              'versioning, and lineage of artifacts',
                  long_description=long_description,
                  author=['Pietro Berkes', 'Samuel Suter'],
                  author_email=['pietro.berkes@nagra.com', 'samuel.suter@nagra.com'],
                  license='ISC',
                  packages=find_packages(),
                  zip_safe=True,
                  setup_requires=['pytest-runner', 'semver'],
                  tests_require=['pytest', 'pytest-custom_exit_code'],
                  install_requires=get_requirements('requirements.txt'),
                  extras_require=extras_require,
                  include_package_data=True,
                  url='https://github.com/nagra-insight/pond',
                  classifiers=[],
                  entry_points={})

setup(**setup_conf)
