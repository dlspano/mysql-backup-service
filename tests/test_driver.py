import filecmp
import paramiko
import os
import re
import unittest

from contextlib import contextmanager
from unittest import mock

# Local imports
from app.drivers import mysqldump


class TestMySQLDumpBackup(unittest.TestCase):
    """
    This unittest tests the functions for the self.backup_client.py script.
    """

    def setUp(self):
        """Setup necessary paths and fixtures"""
        self.local_backup_dir = os.path.join(os.getcwd(),
                                             'tests/local-backups')
        self.remote_backup_dir = '/tmp/backups'
        self.sql_test_file = os.path.join(os.getcwd(), 'tests/files/test.sql')
        self.ssh = mock.MagicMock()
        self.stderr = mock.MagicMock()
        self.stdout = mock.MagicMock()
        self.ssh.exec_command = mock.MagicMock(return_value=('', self.stdout,
                                                             self.stderr))
        self.remote_path = os.path.join(os.getcwd(), 'tests', 'sql-files',
                                        'test-backup.sql.gz')
        self.local_path = os.path.join(os.getcwd(), 'tests', 'local-backups',
                                       'test-backup.sql.gz')
        self.backup_client = mysqldump.MySQLDump(self.ssh)

    @contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            raise self.failureException('{} raised'.format(exc_type.__name__))

    def test_create_local_path(self):
        self.backup_client.create_local_path(self.local_backup_dir)
        self.assertTrue(os.path.exists(self.local_backup_dir))

    def test_create_remote_path(self):
        """Test remote path creation with a mock object"""

        self.stdout.channel.recv_exit_status.return_value = 0
        remote_path = self.backup_client.create_remote_path(
            self.remote_backup_dir)
        self.assertEqual(self.remote_backup_dir, remote_path)

    def test_create_remote_path_negative(self):
        """Test that we handle remote path failures properly"""

        self.stdout.channel.recv_exit_status.return_value = 1
        error_msg = "mkdir: cannot create directory ‘tests’: File exists"
        self.stderr.read.return_value.decode.return_value = error_msg
        remote_path = self.backup_client.create_remote_path(
            self.remote_backup_dir)
        self.assertFalse(remote_path)

    def test_backup_db(self):
        """
        Test that the backup_database function returns the pre-defined
        path if the command executes successfully
        """

        self.stdout.channel.recv_exit_status.return_value = 0
        remote_path = self.backup_client.create_remote_path(
            self.remote_backup_dir)
        self.stdout.channel.recv_exit_status.return_value = 0
        db_backup = self.backup_client.backup_database('test_database',
                                                       remote_path)
        re_string = '/'.join([self.remote_backup_dir, 'test_database'
                             '-\d{2}-\d{2}-\d{4}-\d{2}:\d{2}:\d{2}.sql'])
        regex = re.compile(re_string)
        self.assertTrue(regex.match(db_backup))

    def test_backup_db_negative(self):
        """
        Test that we the backup_database function returns None
        when the command executes unsuccessfully
        """

        self.stdout.channel.recv_exit_status.return_value = 0
        remote_path = self.backup_client.create_remote_path(
            self.remote_backup_dir)
        self.stdout.channel.recv_exit_status.return_value = 1
        error_msg = "mysqldump: permission denied"
        self.stderr.read.return_value.decode.return_value = error_msg
        db_backup = self.backup_client.backup_database('test_database',
                                                       remote_path)
        self.assertIsNone(db_backup)

    def test_backup_db_ssh_exception(self):
        """
        Test that ssh exceptions are caught appropriately.
        """

        self.stdout.channel.recv_exit_status.return_value = 0
        remote_path = self.backup_client.create_remote_path(
              self.remote_backup_dir)
        with self.assertNotRaises(paramiko.SSHException):
            self.ssh.exec_command.side_effect = paramiko.SSHException
            self.backup_client.backup_database('test_database',
                                               remote_path)

    def test_get_backup_file(self):
        """
        Test that we get the database backup file via a
        mock object. Assert that the file is the same as
        our test file.
        """

        self.backup_client.create_local_path(self.local_backup_dir)
        remote_test_file = open(self.remote_path, mode='rb')
        self.ssh.open_sftp.return_value.open.return_value = remote_test_file
        self.backup_client.get_backup_file(self.local_backup_dir,
                                           self.remote_path)
        self.assertTrue(filecmp.cmp(self.remote_path, self.local_path,
                                    shallow=False))

    def test_remote_cleanup(self):
        """Test remote host cleanup with a mock object"""

        self.stdout.channel.recv_exit_status.return_value = 0
        cleanup = self.backup_client.remote_cleanup(
            self.remote_backup_dir)
        self.assertTrue(cleanup)

    def test_cleanup_remote_negative(self):
        """Test that a remote host cleanup failure returns False"""

        self.stdout.channel.recv_exit_status.return_value = 1
        error_msg = "rm: cannot remove 'test-backup.sql.gz': Permission denied"
        self.stderr.read.return_value.decode.return_value = error_msg
        cleanup = self.backup_client.remote_cleanup(
            self.remote_backup_dir)
        self.assertFalse(cleanup)

    def tearDown(self):
        """Clean up leftover resources"""

        if os.path.exists(self.local_backup_dir):
            if os.path.exists(self.local_path):
                os.remove(self.local_path)
            os.rmdir(self.local_backup_dir)


if __name__ == '__main__':
    unittest.main()
