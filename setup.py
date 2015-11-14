import os.path
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

    setup(
        name="whylog",
        version="0.1",
        author="ZPP team",
        author_email="",
        description="whylog v0.1",
        # Space to fill by Ewa
        license="",
        test_requires=[
            'nose',
            'nose-testconfig',
            'test-generator',
        ],
        install_requires = [
        ],
        url="https://github.com/9livesdata/whylog",
        long_description=read('README'),
        classifiers=[
            "Development Status :: 0 - Alpha",
        ],
    )
