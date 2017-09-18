import json
import unittest

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
                            'remote_path': self.app.config['REMOTE_PATH']}

    def test_start_backup(self):
        response = self.client().post('/v1/backup', data=self.backup_data)
        self.assertEqual(response.status_code, 201)

    def test_get_status_by_uuid(self):
        post_response = self.client().post('/v1/backup', data=self.backup_data)
        json_result = json.loads(post_response.data.decode('utf-8').
                                 replace("'", "\""))
        task_id = json_result['task_id']
        get_response = self.client().get('/v1/backup/{}'.format(task_id))
        self.assertEqual(get_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
