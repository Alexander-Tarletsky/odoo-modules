from odoo import fields, models


class CoursePrice(models.Model):
    _name = 'openacademy.course.price'
    _description = "Course Price by Company"
    _rec_name = 'course_id'

    course_id = fields.Many2one(
        comodel_name='openacademy.course',
        string='Course',
        required=True,
        ondelete='cascade',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    price = fields.Monetary(
        string='Price',
        default=0.0,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )

    _sql_constraints = [
        (
            'course_company_unique',
            'UNIQUE(course_id, company_id)',
            "A course can only have one price per company"
        ),
    ]
