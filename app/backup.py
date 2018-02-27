import logging
import paramiko
import os
import shelve
from time import sleep

# Local imports
from app.constants import STATUS, STATUS_FILE_PATH
from app.drivers import mysqldump

LOG = logging.getLogger(__name__)

class Backup:

    def __init__(self, **kwargs):
        self.client = kwargs.get('client')
        self.hostname = kwargs.get('hostname')
        self.username = kwargs.get('username')
        self.database = kwargs.get('database')
        self.local_path = kwargs.get('local_path')
        self.remote_path = kwargs.get('remote_path')
        self.task_uuid = kwargs.get('task_uuid')

    def connect(self):
        """
        Create a connection to the remote host

        :param self.hostname:
        :param self.username:
        :return: ssh
        """

        LOG.info('Trying to connect')
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        LOG.info('hostname {0}'.format(self.hostname))
        ssh.connect(hostname=self.hostname, username=self.username,
                    timeout=180, look_for_keys=True)

        return ssh

    def create(self):
        """
        Create a backup
        :return:
        """
        ssh = self.connect()
        backup_client = None

        if self.client == 'mysqldump':
            backup_client = mysqldump.MySQLDump(ssh)
        backup_client.create_local_path(self.local_path)
        backup_client.create_remote_path(self.remote_path)

        self.status(self.task_uuid, 3)
        backup_file = backup_client.backup_database(self.database,
                                                    self.remote_path)
        compressed_backup = backup_client.compress_db_backup(backup_file)
        if compressed_backup:
            backup_client.get_backup_file(self.local_path,
                                          compressed_backup)
        self.status(self.task_uuid, 0)

    def status(self, task_uuid, status=None):
        """
        An idempotent method that creates or retrieves a task status from
        a shelf database file.
        :param task_uuid:
        :param status:
        :return:
        """
        path = '{0}'.format(STATUS_FILE_PATH)
        if not os.path.exists(path):
            os.makedirs(path)
        path = '{0}/status.txt'.format(path)

        status_file = shelve.open(path)
        if status is not None:
            status_file[task_uuid] = status
        else:
            status = status_file[task_uuid]
        status_file.close()
        return status, STATUS[status]
