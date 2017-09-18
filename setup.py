from setuptools import setup

setup(name = 'safetyculture-sdk-python',
      version = '2.2.0',
      description = 'SafetyCulture Python SDK and iAuditor integration tools',
      url = 'https://github.com/SafetyCulture/safetyculture-sdk-python',
      author = 'SafetyCulture',
      author_email = 'integrations@safetyculture.io',
      include_package_data=True,
      packages = ['safetypy', 'tools', 'tools/exporter'],
      entry_points = {
            'console_scripts': [
                  'iauditor_exporter = tools.exporter.exporter:main',
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
            'future>=0.16.0'
      ],
      )