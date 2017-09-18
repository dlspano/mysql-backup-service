import logging
import paramiko
import uuid

# Local imports
from app.clients import mysqldump

LOG = logging.getLogger(__name__)


class Backup:

    def __init__(self, **kwargs):
        self.client = kwargs['client']
        self.hostname = kwargs['hostname']
        self.username = kwargs['username']
        self.database = kwargs['database']
        self.local_path = kwargs['local_path']
        self.remote_path = kwargs['remote_path']

    def create_connection(self):
        """
        Create a connection to the remote host

        :param hostname:
        :param username:
        :return:
        """

        LOG.info('Trying to connect')
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.hostname, username=self.username,
                    timeout=180, look_for_keys=True)

        return ssh

    def create_backup(self):
        ssh = self.create_connection()
        backup_client = None
        backup_uuid = uuid.uuid4()

        if self.client == 'mysqldump':
            backup_client = mysqldump.MySQLDump(ssh)

        backup_client.create_local_path(self.local_path)
        backup_client.create_remote_path(self.remote_path)
        self.create_status_file(self, backup_uuid)
        backup_file = backup_client.backup_database(self.database,
                                                    self.remote_path)
        compressed_backup = backup_client.compress_db_backup(backup_file)
        if compressed_backup:
            backup_client.get_backup_file(self.local_path, compressed_backup)


#     def create_status_file(self, uuid):
#        """Create a status file where we can keep track of the job"""
