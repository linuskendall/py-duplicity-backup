Backup Tool
----------

Installation steps

1. Unzip package
2. python setup.by build
3. python setup.py install
4. gpg import-key for encryption key
5. gpg gen-key for signing key
6. Add to crontab

Pre-requisites
--------------

Libyaml should be installed to allow for C bindings for yaml interpretation.

Config File
-----------
Should be present either in ~/.backup.cfg /etc/backup.cfg or current directory backup.cfg

[backup]
backup_source: /
backup_dest: file:///tmp/backups
db_backup_dir: /Users/linuskendall/Documents/clients/vizion/db_backups
log_file: duplicity.log

[archives]
# generate new full backups at least weekly
full_if_older_than: 1W
# keep four full backups of incrementals
keep_incrementals_for: 4
# remove backups older than 6 months
remove_older_than: 6M

[s3]
aws_access_key_id:
aws_secret_access_key:

[encryption]
encrypt_key: 
sign_key: 
passphrase: 
sign_passphrase: 

[paths]
mysqldump: /usr/bin/mysqldump
duplicity: /usr/local/bin/duplicity

Backup Destinations
-------------------
Specified in yaml file passed as argument to script:

databases:
  - name: mydb
    user: mydbuser
    password: mydbpass

directories: 
  - /Users/linuskendall/Documents/clients/vizion/backup_source/test.txt
  - /Users/linuskendall/Documents/clients/vizion/backup_source/test_dir/**
  - /Users/linuskendall/Documents/clients/vizion/backup_source/linus/**
  - /Users/linuskendall/Documents/clients/vizion/backup_source/bal/**
