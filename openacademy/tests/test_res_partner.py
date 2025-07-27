"""
Set of tests for ResPartner model
"""
from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestCourseCopyMethod(TransactionCase):
    """Test Case to test the Create and Write methods"""
    def setUp(self, *args, **kwargs):
        super(TestCourseCopyMethod, self).setUp()
        self.Instructor = self.env['res.partner']
        self.test_tag_teacher = self.env.ref('openacademy.partner_tag_teacher')

    def test_create_course_with_set_tag(self):
        """Test create course with set tag"""
        test_instructor_1 = self.Instructor.create({
            'name': "Test Instructor 1",
            'is_instructor': True
        })
        self.assertEqual(
            test_instructor_1.category_id,
            self.test_tag_teacher,
            "Wrong instructor tag",
        )

        test_instructor_2 = self.Instructor.create({
            'name': "Test Instructor 2",
            'is_instructor': False
        })
        self.assertEqual(
            test_instructor_2.category_id.name,
            False,
            "Wrong instructor tag",
        )

    def test_write_course_with_set_tag(self):
        """Test write course with set tag"""
        test_instructor_1 = self.Instructor.create({
            'name': "Test Instructor 1",
        })

        test_instructor_1.write({'is_instructor': True})
        self.assertEqual(
            test_instructor_1.category_id,
            self.test_tag_teacher,
            "Wrong instructor tag",
        )

        test_instructor_1.write({'is_instructor': False})
        self.assertEqual(
            test_instructor_1.category_id.name,
            False,
            "Wrong instructor tag",
        )
