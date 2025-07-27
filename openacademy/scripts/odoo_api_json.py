import random
import requests
import json
import argparse

from typing import Optional, Union, List
from datetime import date, datetime, timedelta


parser = argparse.ArgumentParser()
parser.add_argument("db", type=str, help="database name")  # 'odoo14'
parser.add_argument("user", type=str, help="user name or email")
parser.add_argument("password", type=str, help="password")
parser.add_argument(
    "-u", "--url",
    type=str, default="http://localhost:8069/jsonrpc",
    help="number of sessions (default=http://localhost:8069/jsonrpc)",
)
parser.add_argument(
    "-ns", "--number_of_sessions",
    type=int, default=1,
    help="number of sessions (default=1)",
)
parser.add_argument(
    "-sd", "--start_date",
    type=str, default=date.today().strftime('%Y-%m-%d'),
    help="start date of session ('YYYY-MM-DD')(default - today)",
)
parser.add_argument("-s", "--seats", type=int, default=10, help="seats of session (default=10)")
cmd_args = parser.parse_args()


class SessionsCreator:
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

    def _auth_uid(self) -> str:
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

    def get_instructor_ids_list(self) -> Union[bool, List[str]]:
        """This method checks if there are any instructors at all.
        If they are, then it returns a list of them. Otherwise, it will return False."""
        instructor_ids = self.call(
            'object', 'execute_kw',
            'res.partner', 'search',
            [[['is_instructor', '=', True]]],
        )
        if instructor_ids:
            return instructor_ids
        return False

    def get_course_id(self) -> Union[bool, str]:
        """This method checks if there is such a course. If so, it returns the course id,
        otherwise it returns False"""
        course_id = self.call(
            'object', 'execute_kw',
            'openacademy.course', 'search',
            [[['title', 'ilike', 'python']]],
        )
        if course_id:
            return course_id[0]
        return False

    def get_session_ids_list(self) -> List[str]:
        """This method checks if there is already a session with the same name in the database.
        If they are, then it returns a list of session ids. Otherwise, it will return
        an empty list."""
        course_id = self.get_course_id()
        if not course_id:
            raise AttributeError("Course with the such name is not registered!")
        same_session = self.call(
            'object', 'execute_kw',
            'openacademy.session', 'search',
            [[['course_id', '=', course_id]]],
        )
        if not same_session:
            same_session = []
        return same_session

    def get_start_dates_list(self) -> Union[bool, str, List[str]]:
        date_list = []
        same_session = self.get_session_ids_list()
        if not same_session:
            return False
        else:
            start_date_same_session = self.call(
                'object', 'execute_kw',
                'openacademy.session', 'read',
                [same_session],
                {'fields': ['start_date']}
            )
            if len(same_session) == 1:
                return start_date_same_session[0]['start_date']
            else:
                for item in start_date_same_session:
                    date_list.append(item['start_date'])
                return date_list

    def create_sessions(self, number_of_sessions, start_date, seats) -> Optional[str]:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')  # create object(date)
        list_start_date = self.get_start_dates_list() if self.get_start_dates_list() else []
        new_sessions_id = None

        while number_of_sessions > 0:
            while start_date.strftime('%Y-%m-%d') in list_start_date:  # exclude start_date matches
                start_date += timedelta(days=1)

            new_sessions_id = self.call(
                'object', 'execute_kw',
                'openacademy.session', 'create',
                [{
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'seats': seats,
                    'duration': 10,
                    'course_id': self.get_course_id(),
                    'instructor_id': random.choice(self.get_instructor_ids_list()),
                }],
            )
            start_date += timedelta(days=36)
            number_of_sessions -= 1
            print(f"Create session {new_sessions_id} successful!")
        return new_sessions_id


if __name__ == "__main__":
    create_sessions = SessionsCreator()
    create_sessions.create_sessions(
        cmd_args.number_of_sessions,
        cmd_args.start_date,
        cmd_args.seats)
