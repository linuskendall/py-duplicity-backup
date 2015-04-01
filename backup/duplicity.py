# general includes
import subprocess
import os
import tempfile
import sys

# local imports
import commands

# set up logger
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.FileHandler(commands.LOGFILE)
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

import yaml

# Backup method, runs the backup given the bakcup set in the file backup_Set
def backup(backup_set):
  logger.info("Backup started")

  logger.info("Step 1: Read backup set")
  backup_targets = read_backup_set(backup_set)

  logger.info("Step 2: Write backup targets")
  backup_file = write_backup_list(backup_targets, backup_targets['db_backup_dir'])

  logger.info("Step 3: Run backup")
  run_backup(backup_file.name, backup_targets['backup_source'], backup_targets['backup_dest'])
  os.unlink(backup_file.name)

  logger.info("Step 4: Clean no longer relevant archives")
  clean_old(backup_targets['backup_dest'])

  logger.info("Backup completed")

# reads the config file and gets the target for the backup
def read_backup_set(config_file):
  # dump the databases
  backup_targets = None
  try:
    with open(config_file, 'r') as conf:
      backup_targets = yaml.safe_load(conf)

  except IOError as e:
      logger.error('Could not access backup configuration')
      exit(1)

  logger.info("There are %d databases and %d directories to backup" % (len(backup_targets['databases']), len(backup_targets['directories'])))
  return backup_targets

# write the backup list to duplicity format
def write_backup_list(backup_targets, db_backup_dir):
  # dump the databases to file 
  try: 
    with tempfile.NamedTemporaryFile(delete = False) as backup_list:
      for db in backup_targets['databases']:
        try:
          # set the filename of the generated db file
          db['filename'] = "%s/%s.sql" % (db_backup_dir, db['name'])
          # create the command
          command = [ arg % db for arg in commands.MYSQLDUMP ]
          # run the backup command, capturing output to log
          logger.info(subprocess.check_call(command, stderr=subprocess.STDOUT, env=commands.MYSQLDUMP_ENV))
          # write backup to list
        except subprocess.CalledProcessError as e:
          logger.error('Could not dump db=%s, error=%s' % (db['name'], str(e))) 
        except OSError as e:
          logger.error('Could not dump db=%s, error=%s' % (db['name'], str(e))) 

        # add the filename
        if os.path.exists(db['filename']): 
          backup_list.write('+ %s\n' % db['filename']) 

      # create the included files
      for directory in backup_targets['directories']:
        backup_list.write('+ %s\n' % directory)

      # ignore all other files
      backup_list.write('- **\n')
  except IOError as e:
    logger.error("Couldn't write backup listings file")
    exit(1)

  return backup_list

# run duplicity
def run_backup(backup_file_list, backup_source, backup_dest) :
  # finished writing the file list, now run duplicity
  try:
    logger.info(subprocess.check_call(
      [ arg % { 'backup_file_list': backup_file_list, 'backup_source': backup_source, 'backup_dest': backup_dest } 
        for arg in commands.DUPLICITY],
      stderr=subprocess.STDOUT, 
      env=commands.DUPLICITY_ENV))
  except subprocess.CalledProcessError as e:
    logger.error("Backup did not succeed: %s" % str(e))
  except OSError as e:
    logger.error("Backup did not succeed: %s" % str(e))

def clean_old(backup_dest):
  # after running the backup, lets clean up old backups
  for command in commands.DUPLICITY_CLEAN:
    try:
      logger.info(subprocess.check_call(
        [ arg % { 'backup_dest': backup_dest } 
          for arg in command],
        stderr=subprocess.STDOUT, env=commands.DUPLICITY_ENV))
    except subprocess.CalledProcessError as e:
      logger.error("Clean command did not succeed: %s" % str(e))
    except OSError as e:
      logger.error("Clean command did not succeed: %s" % str(e))

'''
List current status of backup
'''
def collection_status():
  if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    print "Please specify a backup set in YAML format as the argument to this command"
    exit(2)

  backup_targets = read_backup_set(sys.argv[1])
  
  # finished writing the file list, now run duplicity
  try:
    logger.info(subprocess.check_call(
      [ arg % { 'backup_dest': backup_targets['backup_dest'] } 
        for arg in commands.DUPLICITY_COLLECTION_STATUS],
      stderr=subprocess.STDOUT, 
      env=commands.DUPLICITY_ENV))
  except subprocess.CalledProcessError as e:
    logger.error("Collection status did not succeed: %s" % str(e))
  except OSError as e:
    logger.error("Collection status did not succeed: %s" % str(e))

'''
  List backup archive files
'''
def list_files():
  if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    print "Please specify a backup set in YAML format as the argument to this command"
    exit(2)

  backup_targets = read_backup_set(sys.argv[1])
  
  # finished writing the file list, now run duplicity
  try:
    logger.info(subprocess.check_call(
      [ arg % { 'backup_dest': backup_targets['backup_dest'] } 
        for arg in commands.DUPLICITY_LIST_FILES],
      stderr=subprocess.STDOUT, 
      env=commands.DUPLICITY_ENV))
  except subprocess.CalledProcessError as e:
    logger.error("File list did not succeed: %s" % str(e))
  except OSError as e:
    logger.error("File list did not succeed: %s" % str(e))

'''
  Verify a backup archive 
'''
def verify():
  if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    print "Please specify a backup set in YAML format as the argument to this command"
    exit(2)

  backup_targets = read_backup_set(sys.argv[1])
  
  # finished writing the file list, now run duplicity
  try:
    logger.info(subprocess.check_call(
      [ arg % { 'backup_source': backup_targets['backup_source'], 'backup_dest': backup_targets['backup_dest'] } 
        for arg in commands.DUPLICITY_VERIFY],
      stderr=subprocess.STDOUT, 
      env=commands.DUPLICITY_ENV))
  except subprocess.CalledProcessError as e:
    logger.error("Collection status did not succeed: %s" % str(e))
  except OSError as e:
    logger.error("Collection status did not succeed: %s" % str(e))

'''
  Main backup runner
'''
def main():
  if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    print "Please specify a backup set in YAML format as the argument to this command"
    exit(2)

  backup(sys.argv[1])

if __name__ == "__main__":
  main()
