from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='duplicity-backup',
    version='0.5',
    license='Proprietary',
    author='Linus Kendall',
    author_email='me@linuskendall.com',
    long_description='Tool for running backups',
    packages = find_packages(),
    entry_points={
      'console_scripts': [
        'duplicity-backup = backup.duplicity:main',
        ],
      },
    package_data={
      '': [
        'etc/backup.cfg',
        'etc/backup.yml',
        ],
      },
    description='S3 Backup with Duplicity',
    install_requires=['PyYAML'],
)
