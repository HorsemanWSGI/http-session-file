import os
from setuptools import setup, find_packages


version = '0.1'

install_requires = [
    'roughrider.session',
    'cromlech.marshallers',
]

tests_require = [
    'WebTest',
    'pytest',
]

setup(
    name='roughrider.sessions.file',
    version=version,
    description="Session handling for wsgi applications using files",
    long_description=(
        open("README.rst").read() + "\n" +
        open(os.path.join("docs", "HISTORY.rst")).read()),
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='file, session, HTTP',
    author='Souheil Chelfouh',
    author_email='trollfot@gmail.com',
    url='',
    license='ZPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['roughrider', 'roughrider.sessions'],
    include_package_data=True,
    zip_safe=False,
    tests_require=tests_require,
    install_requires=install_requires,
    extras_require={'test': tests_require},
)
