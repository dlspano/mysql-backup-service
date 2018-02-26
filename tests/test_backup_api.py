import json
import paramiko
import unittest

from unittest import mock

# Local imports
from app import create_app


class TestBackupApiV1(unittest.TestCase):
    """Test case for API functionality"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.app = create_app(config_name="development")
        self.client = self.app.test_client
        self.backup_data = {'client': 'mysqldump', 'hostname': 'localhost',
                            'username': 'centos', 'database': 'database1',
                            'local_path': self.app.config['LOCAL_PATH'],
                            'remote_path': self.app.config['REMOTE_PATH'],
                            'task_uuid': 4}
        self.ssh = paramiko.SSHClient()
        self.stdout = mock.MagicMock()
        self.stderr = mock.MagicMock()
        self.ssh.exec_command = mock.MagicMock(return_value=('', self.stdout,
                                                             self.stderr))

    def tearDown(self):
        pass

    @mock.patch('app.backup.Backup.create')
    def test_start_backup(self, mock_create):
        """
        Test a post call too start a backup via the API
        """

        response = self.client().post('/v1/backup', data=self.backup_data)
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(data['task_uuid'],
                         str(self.backup_data.get('task_uuid')))
        self.assertEqual(data['hostname'], self.backup_data.get('hostname'))
        self.assertEqual(data['status'], 4)
        self.assertEqual(response.status_code, 201)

    @mock.patch('app.backup.Backup.status')
    @mock.patch('app.backup.Backup.create')
    def test_get_status_by_uuid(self, mock_status, mock_create):
        """
        Test a get request to the status endpoint
        """

        mock_status.return_value = '0'
        post_response = self.client().post('/v1/backup',
                                           data=self.backup_data)
        data = json.loads(post_response.get_data(as_text=True))
        # json_result = json.loads(post_response.data.decode('utf-8').
        #                          replace("'", "\""))
        task_uuid = data['task_uuid']
        get_response = self.client().get('/v1/backup/{}'.format(
            task_uuid))
        data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(data[status_code], '4')
        self.assertEqual(data[status_code], 'received')
        self.assertEqual(get_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
