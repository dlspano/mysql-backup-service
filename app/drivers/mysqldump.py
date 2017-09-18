import logging
from datetime import datetime

# Local imports
from app.drivers import base

LOG = logging.getLogger(__name__)


class MySQLDump(base.BaseClient):
    """mysqldump client driver class"""

    def backup_database(self, database, directory):
        """
        Use paramiko to run mysql dump on the remote host

        :param ssh:
        :param database:
        :param backup_dir:
        :return back_path:
        """

        backup_time = datetime.now().strftime('%m-%d-%Y-%H:%M:%S')
        path = '{0}/{1}-{2}.sql'.format(directory, database, backup_time)
        mysqldump_cmd = "sudo bash -c 'mysqldump {0} > {1}'".format(database,
                                                                    path)
        try:
            _, stdout, stderr = self.ssh.exec_command(mysqldump_cmd)
            exit_status = stdout.channel.recv_exit_status()
            # We should get an exit status of 1 if the path doesn't exist
            if exit_status > 0:
                LOG.error('Command exit status'
                          ' {0} {1}'.format(exit_status,
                                            stderr.read().decode()))
                return None
            return path
        except self.paramiko.ssh_exception.SSHException as e:
            LOG.error('Connection to host failed with error'
                      '{0}'.format(e))
