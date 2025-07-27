"""
Set of tests for Course model
"""
from datetime import date

from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger
from psycopg2 import IntegrityError


@tagged('-at_install', 'post_install')
class TestCourseName(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestCourseName, self).setUp()
        self.Course = self.env['openacademy.course']

    def test_unique_name_constraints(self):
        """Checking the title of the course for uniqueness"""
        self.Course.create({'title': 'Course 1'})
        with mute_logger('odoo.sql_db'):
            # self.assertRaises(IntegrityError, self.Course.create, {'title': 'Course 1'})
            with self.assertRaises(IntegrityError):
                self.Course.create({'title': 'Course 1'})


@tagged('-at_install', 'post_install')
class TestCourseState(TransactionCase):
    """Test Case to test a course activation and deactivation"""
    def setUp(self, *args, **kwargs):
        super(TestCourseState, self).setUp()
        self.test_course = self.env['openacademy.course'].create({'title': 'Course 1'})

    def test_state_course(self):
        self.assertEqual(
            self.test_course.active,
            True,
            "The 'active' field should be True")
        self.assertEqual(
            self.test_course.state,
            'active',
            "Course state should be changed to active")

        self.test_course.move_to_archive()

        self.assertEqual(
            self.test_course.active,
            False,
            "The 'active' field should be False")
        self.assertEqual(
            self.test_course.state,
            'inactive',
            "Course state should be changed to inactive")

        self.test_course.restore_from_archive()

        self.assertEqual(
            self.test_course.active,
            True,
            "The 'active' field should be True")
        self.assertEqual(
            self.test_course.state,
            'active',
            "Course state should be changed to active")


@tagged('-at_install', 'post_install')
class TestCourseCopyMethod(TransactionCase):
    """Test Case to test the Copy method"""
    def setUp(self, *args, **kwargs):
        super(TestCourseCopyMethod, self).setUp()
        self.test_course = self.env['openacademy.course'].create({'title': 'Course_1'})

    def test_one_copy_course(self):
        test_copy_course_1 = self.test_course.copy()
        self.assertEqual(
            test_copy_course_1.title,
            "Duplicate of {}".format(self.test_course.title),
            "Course title should be Duplicate of {}".format(self.test_course.title))

    def test_double_copy_course(self):
        self.test_course.copy()
        test_copy_course_2 = self.test_course.copy()
        self.assertEqual(
            test_copy_course_2.title,
            "Duplicate of {} ({})".format(self.test_course.title, 2),
            "Course title should be Duplicate of {} ({})".format(self.test_course.title, 2))

    def test_copy_of_copy_course(self):
        test_copy_course_1 = self.test_course.copy()
        test_copy_of_copy_course_1 = test_copy_course_1.copy()
        self.assertEqual(
            test_copy_of_copy_course_1.title,
            "Duplicate of Duplicate of {}".format(self.test_course.title),
            "Course title should be Duplicate of Duplicate of {}".format(self.test_course.title))


@tagged('-at_install', 'post_install')
class TestCoursePrice(TransactionCase):
    """Test case tests the behavior of the Course.price field for different companies"""
    def setUp(self, *args, **kwargs):
        super(TestCoursePrice, self).setUp()
        self.test_company_1 = self.env['res.company'].create({'name': "Test Company 1"})
        self.test_company_2 = self.env['res.company'].create({'name': "Test Company 2"})
        self.Course = self.env['openacademy.course']

    def test_check_price(self):
        self.test_course = self.Course.create(
            {'title': 'Test Course 1'})

        self.test_course.with_company(self.test_company_1).price = 10

        self.assertEqual(
            self.test_course.with_company(self.test_company_1).price,
            10,
            "Wrong course price")

        self.assertEqual(
            self.test_course.with_company(self.test_company_2).price,
            0,
            "Wrong course price")


@tagged('-at_install', 'post_install')
class TestSessionOnlyCurrentCompany(TransactionCase):
    """Test case test of displaying sessions of the current company only
    and default setting for the session of the current company"""
    def setUp(self, *args, **kwargs):
        super(TestSessionOnlyCurrentCompany, self).setUp()
        self.test_company_1 = self.env['res.company'].create({'name': "Test Company 1"})
        self.test_company_2 = self.env['res.company'].create({'name': "Test Company 2"})
        self.Instructor = self.env['res.partner']
        self.test_course = self.env['openacademy.course'].create({'title': 'Test Course 1'})
        self.Session = self.env['openacademy.session']

    def test_view_company_session(self):
        test_instructor_1 = self.Instructor.with_company(self.test_company_1).create({
            'name': "Test Instructor 1",
            'is_instructor': True,
        })
        test_instructor_2 = self.Instructor.with_company(self.test_company_2).create({
            'name': "Test Instructor 1",
            'is_instructor': True,
        })
        test_session_1 = self.Session.with_company(self.test_company_1).create({
            'start_date': date.today(),
            'course_id': self.test_course.id,
            'instructor_id': test_instructor_1.id,
        })
        test_session_2 = self.Session.with_company(self.test_company_2).create({
            'start_date': date.today(),
            'course_id': self.test_course.id,
            'instructor_id': test_instructor_2.id,
        })

        self.test_course.invalidate_cache()
        self.assertEqual(
            self.test_course.with_company(self.test_company_1).session_ids,
            test_session_1,
            "Wrong Course.session_ids field",
        )

        self.test_course.invalidate_cache()
        self.assertEqual(
            self.test_course.with_company(self.test_company_2).session_ids,
            test_session_2,
            "Wrong Course.session_ids field",
        )

    def test_set_session_default_company(self):
        test_instructor_1 = self.Instructor.create({
            'name': "Test Instructor 1",
            'is_instructor': True,
        })

        test_session_1 = self.Session.create({
            'start_date': date.today(),
            'seats': 10,
            'course_id': self.test_course.id,
            'instructor_id': test_instructor_1.id,
        })

        self.assertEqual(
            test_session_1.company_id,
            self.env.company,
            "Wrong Session.company_id field",
        )
