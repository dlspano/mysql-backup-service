import paramiko
import logging
import os


LOG = logging.getLogger(__name__)


class BaseClient:
    """Base driver class for backup client drivers"""

    def __init__(self, ssh):
        self.ssh = ssh

    def backup_database(self, database, directory):
        pass

    def compress_db_backup(self, path):
        """
        Compress backup file with remote host's gzip command

        :param ssh:
        :param path:
        :return:
        """

        compress_cmd = 'sudo gzip {0}'.format(path)
        compressed_path = '{0}.gz'.format(path)
        file_list_output = ''

        try:
            _, stdout, _ = self.ssh.exec_command(compress_cmd)
            LOG.info('stdout: {0}'.format(stdout.read().decode()))
            _, stdout, _ = self.ssh.exec_command('ls {0}'.format(
                compressed_path))
            file_list_output = stdout.read().decode()
            LOG.info('file_list: {0}'.format(file_list_output))
        except paramiko.ssh_exception.SSHException as e:
            LOG.error('Connection to host failed with error'
                      '{0}'.format(e))

        if compressed_path in file_list_output:
            return compressed_path
        else:
            return None

    def create_local_path(self, path):
        """
        Create local path for backups

        :param path:
        """

        if not os.path.exists(path):
            os.makedirs(path)

    def create_remote_path(self, path):
        """
        Create remote backup path if it doesn't exist

        :param path:
        :return: path
        """
        create_path_cmd = 'sudo mkdir -p {0}'.format(path)
        try:
            _, stdout, stderr = self.ssh.exec_command(create_path_cmd)
            exit_status = stdout.channel.recv_exit_status()

            # We should get an exit status of 1 if the path doesn't exist
            if exit_status > 0:
                LOG.error('Command exit status'
                          ' {0} {1}'.format(exit_status,
                                            stderr.read().decode()))
                return None
            return path
        except paramiko.ssh_exception.SSHException as e:
            LOG.error('Connection to host failed with error'
                      '{0}'.format(e))

    def get_backup_file(self, local_path, remote_path):
        """
        Retrieve backup file from database host

        :param local_path:
        :param remote_path:
        :return: boolean
        """

        sftp = self.ssh.open_sftp()
        backup_file = remote_path.split('/')[-1]
        local_path = '/'.join([local_path, backup_file])

        try:
            with sftp.open(remote_path, mode='rb') as remote_file:
                contents = remote_file.read()
            with open(local_path, 'wb') as local_file:
                local_file.write(contents)
                return True
        except paramiko.ssh_exception.SSHException as e:
            LOG.error('Connection to host failed with error'
                      '{0}'.format(e))

    def remote_cleanup(self, remote_path):
        """
        Cleanup remote host backup directory

        :param remote_path:
        :return: boolean
        """

        cleanup_cmd = 'sudo rm -f {0}'.format(remote_path)
        try:
            _, stdout, stderr = self.ssh.exec_command(cleanup_cmd)
            exit_status = stdout.channel.recv_exit_status()

            # We should get an exit status of 1 if the path doesn't exist
            if exit_status > 0:
                LOG.error('Command exit status'
                          ' {0} {1}'.format(exit_status,
                                            stderr.read().decode()))
                return False
            return True
        except paramiko.ssh_exception.SSHException as e:
            LOG.error('Connection to host failed with error'
                      '{0}'.format(e))

    def run_command(self, command):
        """
        A wrapper command for paramiko commands

        :param ssh:
        :param command:
        :return :
        """

        try:
            _, stdout, stderr = self.ssh.exec_command(command)

            exit_status = stdout.channel.recv_exit_status()
            # We should get an exit status of 1 if the path doesn't exis
            if exit_status > 0:
                LOG.error('Command exit status'
                          ' {0} {1}'.format(exit_status,
                                            stderr.read().decode()))

            return exit_status
        except paramiko.ssh_exception.SSHException as e:
            LOG.error('Connection to host failed with error'
                      '{0}'.format(e))
