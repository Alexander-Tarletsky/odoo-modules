import json
from datetime import datetime

from odoo import http
from odoo.http import request, Response


class CourseController(http.Controller):
    @http.route('/openacademy/courses', type='http', auth='public', method=['GET'])
    def get_courses(self, title=None, start_date=None, available_seats=None, **kwargs):
        headers = {'Content-Type': 'application/json'}
        domain_course = []
        payload = {}
        filtered_courses = []

        if title:
            title = str(title)
            domain_course.append(['title', 'ilike', title])

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError as err:
                payload['error'] = {"Invalid date format": str(err)}
            domain_course.append(['session_ids.start_date', '=', start_date])

        if available_seats:
            if not payload.get('error'):
                try:
                    available_seats = int(available_seats)
                except ValueError as err:
                    payload = {'error': {"Wrong available seats parameter value": str(err)}}

                courses = request.env['openacademy.course'].search(domain_course)
                for course in courses:
                    for session in course.session_ids:
                        if session.seats - session.number_attendees >= available_seats:
                            filtered_courses += course
                            break

        if not payload.get('error'):
            payload = {'data': [{
                'id': c.id,
                'title': c.title,
                'active': c.active
            } for c in filtered_courses]}

        return Response(json.dumps(payload), headers=headers)

    @http.route(
        '/openacademy/courses/report',
        type='http',
        auth='public',
        website=True,
        method=['GET']
    )
    def display_courses(self, **kwargs):
        if request.env.user.login == 'public':
            courses = request.env['openacademy.course'].search(['active', '=', True])
        else:
            courses = request.env['openacademy.course'].search([])

        payload = {'data': [{
            'id': c.id,
            'title': c.title,
            'sessions': [{
                'start_date': s.start_date.strftime('%Y-%m-%d'),
                'duration': s.duration,
                'seats': s.seats,
                'number_attendees': s.number_attendees,
                'instructor': s.instructor_id.name
            } for s in c.session_ids]
        } for c in courses]}

        return request.render('openacademy.courses_details_page', {'queryset': payload})

    @http.route(
        '/openacademy/sessions/<int:session_id>/add_listener',
        type='json',
        auth='user',
        method=['POST'],
    )
    def add_attendees(self, session_id=None, **kwargs):
        session = request.env['openacademy.session'].search([['id', '=', session_id]])
        if not session:
            return {
                'status': 'failed',
                'error': "Session not found",
            }

        if not request.env.user.has_group('openacademy.openacademy_manager_group') and \
                session.course_id.responsible_id.login != request.env.user.login and \
                session.course_id.responsible_id:
            return {
                "status": "failed",
                "error": "You do not have access rights to modify sessions!",
            }

        data = request.jsonrequest
        if 'name' not in data:
            return {
                "status": "failed",
                "error": "Json request must have the key 'name'!",
            }

        session_listener = request.env['res.partner'].search([['name', '=', data.get('name')]])
        if not session_listener:
            session_listener = request.env['res.partner'].create({
                'name': data.get('name'),
                'is_instructor': False,
            })

        session.attendee_ids += session_listener

        return {"status": "success"}
