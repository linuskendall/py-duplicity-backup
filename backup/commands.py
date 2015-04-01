#!python
import os
import ConfigParser

# Read config file
cp = ConfigParser.ConfigParser()
cp.read(['/etc/backup.cfg', os.path.expanduser('~/.backup.cfg'), 'backup.cfg'])

# LOGFILE
LOGFILE=cp.get("backup", "log_file")

# Settings for database backups
MYSQLDUMP_ENV= { }
MYSQLDUMP = [cp.get('paths', 'mysqldump'), "--user=%(user)s", "--password=%(password)s", "--result-file=%(filename)s", "%(name)s"]

# Environment variables to pass to duplicity
DUPLICITY_ENV = { 
  'PATH': os.environ['PATH']
}

# extra args for all commands
EXTRA_ARGS = []
# extra args only for backup
BACKUP_EXTRA_ARGS = []

if cp.has_option('encryption', 'passphrase'):
  DUPLICITY_ENV['PASSPHRASE'] = cp.get("encryption", "passphrase")

if cp.has_option('encryption', 'sign_passphrase'):
  DUPLICITY_ENV['SIGN_PASSPHRASE'] = cp.get("encryption", "sign_passphrase")

if cp.has_section('s3'):
  DUPLICITY_ENV['AWS_ACCESS_KEY_ID'] = cp.get("s3", "aws_access_key_id")
  DUPLICITY_ENV['AWS_SECRET_ACCESS_KEY'] = cp.get("s3", "aws_secret_access_key")

if cp.has_section('ftp'):
  if cp.has_option('ftp', 'password'):
    DUPLICITY_ENV['FTP_PASSWORD'] = cp.get("ftp", "password")
    EXTRA_ARGS.append('--ssh-askpass')
  if cp.has_option('ftp','identity_file'):
    EXTRA_ARGS += ['--ssh-options', '-oIdentityFile=%s' % cp.get('ftp','identity_file')]

if cp.has_section('encryption.additional_keys'):
  for key in cp.options('encryption.additional_keys'):
    BACKUP_EXTRA_ARGS += ['--encrypt-key', cp.get('encryption.additional_keys', key)]


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
  ] + EXTRA_ARGS + BACKUP_EXTRA_ARGS

# Clean is a list of commands to run to clear old backups
# with these settings we'll keep weekly archives for 6 months
# daily archives for 4 weeks
DUPLICITY_CLEAN = [
  # remove backups after 6 months
  [ cp.get("paths", "duplicity"), "remove-older-than", cp.get("archives","remove_older_than"), "--force", "%(backup_dest)s" ] + EXTRA_ARGS,
  # Keep incremental copies for the last 4 , since we keep full copies each week, this means 4 weeks of incremental copies to be ketp
  [ cp.get("paths", "duplicity"), "remove-all-inc-of-but-n-full",cp.get("archives","keep_incrementals_for"), "--force", "%(backup_dest)s" ] + EXTRA_ARGS, 
]

DUPLICITY_COLLECTION_STATUS = [
  cp.get("paths", "duplicity"), "collection-status", "%(backup_dest)s",
] + EXTRA_ARGS

DUPLICITY_LIST_FILES = [
  cp.get("paths", "duplicity"), "list-current-files", "%(backup_dest)s",
] + EXTRA_ARGS

DUPLICITY_VERIFY  = [
  cp.get("paths", "duplicity"), "verify", "--include-globbing-filelist=%(backup_file_list)s", "%(backup_dest)s", "%(backup_source)s", 
] + EXTRA_ARGS

DUPLICITY_RESTORE = [
    cp.get("paths", "duplicity"), "restore", "--file-to-restore", "%(file_to_restore)s", "%(backup_dest)s", "%(destination)s",
] + EXTRA_ARGS
