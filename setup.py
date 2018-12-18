from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='texthammer-parsing',
      version=version,
      description="Tools and shortcuts for programmatically running dependency parsers for multiple languages to produce xml output",
      long_description="""\
Tools and shortcuts for programmatically running dependency parsers for multiple languages to produce xml output""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='corpora parsers xml parsing',
      author='Juho Härme',
      author_email='juho.harme@gmail.com',
      url='https://github.com/utacorpora/texthammer-parsing',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'wheel',
          'lxml',
          'progressbar2'
      ],
      entry_points={
          'console_scripts': [
              'texthammerparsing = texthammerparsing.texthammerparsing:main'
              ]
          }
      )
