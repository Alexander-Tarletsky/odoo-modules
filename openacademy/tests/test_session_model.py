"""
Set of tests for Session model
"""
from datetime import date, timedelta

from odoo import exceptions
from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestSessionAttendee(TransactionCase):
    """Test Case implements a check for adding a session instructor and attendee"""

    def setUp(self, *args, **kwargs):
        super(TestSessionAttendee, self).setUp()
        self.test_course = self.env['openacademy.course'].create({'title': 'Course 1'})
        self.test_session = self.env['openacademy.session']
        self.test_attendee = self.env['res.partner']

    def test_check_instructor(self):
        """Check for adding an incorrect session instructor"""
        false_instructor = self.test_attendee.create({
            'name': "Test Instructor 1",
            'is_instructor': False,
        })

        with self.assertRaises(exceptions.ValidationError) as e_cm:
            self.test_session.create({
                'start_date': date.today().strftime('%Y-%m-%d'),
                'seats': 10,
                'course_id': self.test_course.id,
                'instructor_id': false_instructor.id,
            })
        self.assertEqual(
            str(e_cm.exception),
            "Error adding session instructor! This participant is not an instructor",
            "Wrong error message",
        )

    def test_check_attendee(self):
        """Check for adding an incorrect session attendee"""
        instructor = self.test_attendee.create({
            'name': "Test Instructor 1",
            'is_instructor': True,
        })
        incorrect_attendee = self.test_attendee.create({
            'name': "Test Attendee 1",
            'is_instructor': True,
        })

        with self.assertRaises(exceptions.ValidationError) as e_cm:
            self.test_session.create({
                'start_date': date.today().strftime('%Y-%m-%d'),
                'seats': 10,
                'course_id': self.test_course.id,
                'instructor_id': instructor.id,
                'attendee_ids': [incorrect_attendee.id],
            })
        self.assertEqual(
            str(e_cm.exception),
            "Error adding session attendee! Instructor cannot be a attendee",
            "Wrong error message",
        )


@tagged('-at_install', 'post_install')
class TestSessionDate(TransactionCase):
    """Test Case implements verification of setting dates and seats for sessions"""

    def setUp(self, *args, **kwargs):
        super(TestSessionDate, self).setUp()
        self.test_course = self.env['openacademy.course'].create({'title': 'Course 1'})

        self.test_instructor = self.env['res.partner'].create({
            'name': "Test Instructor 1",
            'is_instructor': True,
        })
        self.test_attendees = self.env['res.partner'].create([
            {'name': "Test Attendee 1", 'is_instructor': False},
            {'name': "Test Attendee 2", 'is_instructor': False},
        ])
        self.test_session = self.env['openacademy.session'].create({
            'start_date': date.today(),
            'seats': 10,
            'course_id': self.test_course.id,
            'instructor_id': self.test_instructor.id,
        })

    def test_check_date(self):
        """Test for setting an incorrect dates of session"""
        self.test_session['end_date'] = date.today() - timedelta(days=2)

        with self.assertRaises(exceptions.UserError) as e_cm:
            self.test_session._check_date()
        self.assertEqual(
            str(e_cm.exception),
            "Duration cannot be negative",
            "Wrong error message",
        )

    def test_check_seats(self):
        """Test for setting an incorrect seats of session"""
        self.test_session.seats = -2
        with self.assertRaises(exceptions.UserError) as e_cm:
            self.test_session._check_seats()
        self.assertEqual(
            str(e_cm.exception),
            "Number of seats should be more than number of participants",
            "Wrong error message",
        )

        self.test_session.seats = 1
        self.test_session.attendee_ids = self.test_attendees.ids

        with self.assertRaises(exceptions.UserError) as e_cm:
            self.test_session._check_seats()
        self.assertEqual(
            str(e_cm.exception),
            "Number of seats should be more than number of participants",
            "Wrong error message",
        )

    def test_compute_number_attendees(self):
        """Test compute number attendees"""
        self.test_session.attendee_ids = self.test_attendees.ids
        self.test_session._compute_number_attendees()
        self.assertEqual(
            self.test_session.number_attendees,
            2,
            "Wrong number attendees",
        )

    def test_inverse_end_date(self):
        """Test compute inverse end date"""
        self.test_session.end_date = date.today() + timedelta(days=5)
        self.test_session._inverse_end_date()
        self.assertEqual(
            self.test_session.duration,
            5,
            "Wrong compute inverse end date",
        )

    def test_compute_end_date(self):
        """Test compute end date"""
        self.test_session.duration = 6
        self.test_session._compute_end_date()
        self.assertEqual(
            self.test_session.end_date,
            date.today() + timedelta(days=6),
            "Wrong compute end date",
        )

    def test_compute_taken_percentage(self):
        """Test compute taken percentage"""
        self.assertEqual(
            self.test_session.taken_percentage,
            0,
            "Wrong compute taken percentage",
        )

        self.test_session.attendee_ids = [self.test_attendees[0].id]
        self.assertEqual(
            self.test_session.taken_percentage,
            10,
            "Wrong compute taken percentage",
        )

        self.test_session.attendee_ids = self.test_attendees.ids
        self.assertEqual(
            self.test_session.taken_percentage,
            20,
            "Wrong compute taken percentage",
        )


@tagged('-at_install', 'post_install')
class TestSessionInstructorOnlyCurrentCompany(TransactionCase):
    """Test case test of displaying sessions of the current company only"""
    def setUp(self, *args, **kwargs):
        super(TestSessionInstructorOnlyCurrentCompany, self).setUp()
        self.test_company_1 = self.env['res.company'].create({'name': "Test Company 1"})
        self.test_company_2 = self.env['res.company'].create({'name': "Test Company 2"})
        self.Instructor = self.env['res.partner']
        self.test_course = self.env['openacademy.course'].create({'title': 'Test Course 1'})
        self.Session = self.env['openacademy.session']

    def test_set_session_instructor(self):
        test_instructor_1 = self.Instructor.create({
            'name': "Test Instructor 1",
            'is_instructor': True,
            'company_id': self.test_company_1.id,
        })
        test_instructor_2 = self.Instructor.create({
            'name': "Test Instructor 2",
            'is_instructor': True,
            'company_id': self.test_company_2.id,
        })

        test_session_1 = self.Session.create({
            'start_date': date.today(),
            'course_id': self.test_course.id,
            'instructor_id': test_instructor_1.id,
            'company_id': self.test_company_1.id,
        })

        with self.assertRaises(exceptions.UserError):
            test_session_1.instructor_id = test_instructor_2.id
