from setuptools import setup

setup(name = 'safetyculture-sdk-python',
      version = '3.1.4',
      description = 'iAuditor Python SDK and integration tools',
      url = 'https://github.com/SafetyCulture/safetyculture-sdk-python',
      author = 'SafetyCulture',
      author_email = 'integrations@safetyculture.io',
      include_package_data=True,
      packages = ['safetypy', 'tools', 'tools/exporter', 'tools/import_grs'],
      entry_points = {
            'console_scripts': [
                  'iauditor_exporter = tools.exporter.exporter:main',
                  'import_grs = tools.import_grs.import_grs:main'
            ],
      },
      long_description=open('README.md', 'r').read(),
      install_requires = [
            'python-dateutil>=2.5.0',
            'pytz>=2015.7',
            'tzlocal>=1.3',
            'unicodecsv>=0.14.1',
            'requests>=2.10.0',
            'pyyaml>=3.11',
            'future>=0.16.0',
            'xlrd==1.1.0'
      ],
      )