import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

requires = [
]

setup(name='homerun',
      version='0.0',
      description='module to interface with Silicon Dust\'s HD Homerun',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        ],
      author='',
      author_email='',
      url='',
      keywords='',
      packages=find_packages(),
      include_package_data=False,
      zip_safe=True,
      test_suite='homerun',
      install_requires=requires,
      entry_points="""\
      """,
      )

