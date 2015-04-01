from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='duplicity-backup',
    version='0.9',
    license='GPLv2',
    author='Linus Kendall',
    author_email='me@linuskendall.com',
    long_description='Tool for running backups',
    packages = find_packages(),
    entry_points={
      'console_scripts': [
        'duplicity-backup = backup.duplicity:main',
        'duplicity-restore = backup.duplicity:restore',
        'duplicity-status = backup.duplicity:collection_status',
        'duplicity-verify = backup.duplicity:verify',
        'duplicity-list-files = backup.duplicity:list_files',
        ],
      },
    package_data={
      '': [
        'etc/backup.cfg',
        'etc/backup.yml',
        ],
      },
    description='Backups with Duplicity',
    install_requires=['PyYAML'],
)
