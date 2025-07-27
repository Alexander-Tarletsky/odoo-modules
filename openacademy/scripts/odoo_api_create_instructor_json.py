import os
import requests
import json
import base64
import argparse

from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("db", type=str, help="database name")  # 'odoo14'
parser.add_argument("user", type=str, help="user name or email")
parser.add_argument("password", type=str, help="password")
parser.add_argument(
    "-u", "--url",
    type=str, default="http://localhost:8069/jsonrpc",
    help="number of sessions (default - http://localhost:8069/jsonrpc)",
)
parser.add_argument(
    "-name", "--instructor_name",
    type=str, default='Name unknown',
    help="instructor name (default - Name unknown)",
)
parser.add_argument(
    "-pi", "--path_to_image",
    type=str, default="/home/ventortech/Pictures/image.png",
    help="path to images (default: /home/ventortech/Pictures//image.png)",
)
cmd_args = parser.parse_args()


class InstructorCreator:
    def __init__(self):
        self.url = cmd_args.url
        self.db = cmd_args.db
        self.user = cmd_args.user
        self._password = cmd_args.password
        self.uid = self._auth_uid()

    def json_rpc(self, method, params):
        headers = {'content-type': 'application/json'}
        _id = int(round(datetime.now().timestamp()))
        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': _id,
        }

        response = requests.post(self.url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        if response.json().get('error'):
            raise Exception(response.json()['error']['message'])

        return response.json()['result']

    def call(self, service, method, *args):
        _args = (self.db, self.uid, self._password) + args
        params = {
            'service': service,  # common or object
            'method': method,  # execute_kw / login /
            'args': _args,
        }

        return self.json_rpc('call', params=params)

    def _auth_uid(self):
        uid_args = (self.db, self.user, self._password)
        params = {
            'service': 'common',  # common or object
            'method': 'login',  # execute_kw / login /
            'args': uid_args,
        }
        uid = self.json_rpc('call', params=params)
        if not uid:
            raise AttributeError("Invalid authentication parameters!")
        return uid

    def category_id(self):
        category_id = self.call(
            'object', 'execute_kw',
            'res.partner.category', 'search',
            [[['name', 'ilike', 'teacher']]],
        )
        if category_id:
            return category_id
        return False

    def create_instructor(self, name, image):
        if not os.path.exists(image):
            raise OSError("Invalid path or filename", image)

        with open(image, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read())
        instructor = self.call(
            'object', 'execute_kw',
            'res.partner', 'create',
            [{
                'name': name,
                'is_instructor': True,
                'category_id': self.category_id() if self.category_id() else None,
                'image_1920': encoded_image.decode('utf-8'),
            }],
        )
        print(f"Create instructor {instructor} successful!")
        return instructor


if __name__ == "__main__":
    create_instructor = InstructorCreator()
    create_instructor.create_instructor(cmd_args.instructor_name, cmd_args.path_to_image)
