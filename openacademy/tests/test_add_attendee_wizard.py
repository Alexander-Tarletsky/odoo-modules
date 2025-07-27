"""
Set of tests for Add Attendee Wizard
"""
from datetime import date

from odoo import exceptions
from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestAddAttendeeWizard(TransactionCase):
    """
    Test Cases related to AddAttendeeWizard(`openacademy.add_attendee_wizard`)
    """
    def setUp(self, *args, **kwargs):
        """
        Prepare environment to unit tests
        """
        super(TestAddAttendeeWizard, self).setUp()
        self.test_course = self.env['openacademy.course'].create({'title': "Test Course 1"})
        self.test_instructor = self.env['res.partner'].create({
            'name': "Test Instructor 1",
            'is_instructor': True,
        })
        self.test_sessions = self.env['openacademy.session'].create([
            {
                'start_date': date.today(),
                'seats': 1,
                'course_id': self.test_course.id,
                'instructor_id': self.test_instructor.id,
            },
            {
                'start_date': date.today(),
                'seats': 1,
                'course_id': self.test_course.id,
                'instructor_id': self.test_instructor.id,
            },
        ])
        self.Attendee = self.env['res.partner']
        self.Wizard = self.env['openacademy.add_attendee_wizard']

    def test_add_attendee_to_multiple_sessions(self):
        """
        Add attendee to 2 sessions at a time. Check that attendee was added
        """
        attendee = self.Attendee.create({
            'name': "Test Attendee 1",
            'is_instructor': False,
        })

        wizard = self.Wizard.create({'session_ids': self.test_sessions.ids})

        wizard.attendee_ids = [attendee.id]
        wizard.add_attendee()

        for n, session in enumerate(self.test_sessions):
            self.assertEqual(
                session.attendee_ids,
                attendee,
                "Attendee is not equal for session_{}".format(n),
            )

    def test_add_attendee_for_session_with_attendee(self):
        """
        Add attendee to two sessions one of which already has a attendee.
        Check that error will be raised
        """
        attendee_1 = self.Attendee.create({
            'name': "Test Attendee 1",
            'is_instructor': False,
        })

        attendee_2 = self.Attendee.create({
            'name': "Test Attendee 2",
            'is_instructor': False,
        })

        self.test_sessions.attendee_ids = attendee_1

        wizard = self.Wizard.create({'session_ids': self.test_sessions})
        wizard.attendee_ids = attendee_2

        with self.assertRaises(exceptions.ValidationError) as e_cm:
            wizard.add_attendee()
        self.assertEqual(
            str(e_cm.exception),
            "Error adding attendee. The number of seats for this session in the {}"
            "programming course has been exceeded.".format("Test Course 1"),
            "Wrong error message",
        )

    def test_add_active_sessions_from_context(self):
        """Test add active sessions from context"""
        context = dict(self.env.context)
        context.update({'active_ids': self.test_sessions.ids})
        self.env.context = context

        self.assertEqual(
            self.env.context.get('active_ids'),
            self.Wizard._default_sessions().ids,
            "'_default_sessions' method worked incorrectly",
        )
