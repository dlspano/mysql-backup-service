import uuid
from flask_api import FlaskAPI
from flask import request, jsonify
from multiprocessing import Process

# Local imports
from instance.config import app_config


def create_app(config_name):
    from app.backup import Backup
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    @app.route('/v1/backup', methods=['POST'])
    def backup_create():
        if request.method == 'POST':
            backup_data = request.data
            app.logger.info('hostname {0}'.format(backup_data.get('hostname')))
            server_backup = Backup(**backup_data)
            backup_proc = Process(target=server_backup.create())
            backup_proc.start()
            response = jsonify({
                'task_uuid': backup_data.get('task_uuid'),
                'hostname': backup_data.get('hostname'),
                'status': 4
            })
            response.status_code = 201
            return response

    @app.route('/v1/backup/<uuid:task_id>/', methods=['GET'])
    def get_backup_status(task_id):
        if request.method == 'GET':
            # data = request.data
            backup = Backup()
            status_code, status = backup.status(task_uuid=task_id)
            response = jsonify({
                'status_code': status_code,
                'status': status
            })
            response.status_code = 201
            return response
    return app
