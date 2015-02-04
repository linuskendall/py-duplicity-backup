#!python
import os
import ConfigParser

# Read config file
cp = ConfigParser.ConfigParser()
cp.read(['/etc/backup.cfg', os.path.expanduser('~/.backup.cfg'), 'backup.cfg'])

# LOGFILE
LOGFILE=cp.get("backup", "log_file")

# Where we'll write the backup targets
BACKUP_SOURCE=cp.get('backup', 'backup_source')
# s3+http://bucket_name
BACKUP_DEST=cp.get('backup', 'backup_dest')

# Settings for database backups
DB_BACKUP_DIR=cp.get('backup', 'db_backup_dir')
MYSQLDUMP_ENV= { }
MYSQLDUMP = [cp.get('paths', 'mysqldump'), "--user=%(user)s", "--password=%(password)s", "--result-file=%(filename)s", "%(name)s"]

# Environment variables to pass to duplicity
DUPLICITY_ENV= { 
  'PATH': os.environ['PATH'], 
  'PASSPHRASE': cp.get("encryption", "passphrase"), 
  'SIGN_PASSPHRASE': cp.get("encryption", "sign_passphrase"),
  'AWS_ACCESS_KEY_ID': cp.get("s3", "aws_access_key_id"),
  'AWS_SECRET_ACCESS_KEY': cp.get("s3", "aws_secret_access_key"),
}

# This is the actual backup command
# "--log-file", LOGFILE,
DUPLICITY = [
  cp.get("paths", "duplicity"), 
  "-v4",
  "--encrypt-key", cp.get("encryption", "encrypt_key"),
  "--sign-key", cp.get("encryption", "sign_key"),
  "--full-if-older-than", cp.get("archives", "full_if_older_than"),
  "--include-globbing-filelist=%(backup_file_list)s",
  "%(backup_source)s", "%(backup_dest)s",
  ]

# Clean is a list of commands to run to clear old backups
# with these settings we'll keep weekly archives for 6 months
# daily archives for 4 weeks
DUPLICITY_CLEAN = [
  # remove backups after 6 months
  [ "duplicity", "remove-older-than", cp.get("archives","remove_older_than"), "--force", "%(backup_dest)s" ],
  # Keep incremental copies for the last 4 , since we keep full copies each week, this means 4 weeks of incremental copies to be ketp
  [ "duplicity", "remove-all-inc-of-but-n-full",cp.get("archives","keep_incrementals_for"), "--force", "%(backup_dest)s" ], 
]
