from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    company_is_open = fields.Boolean(
        string='Is library open?',
        default=True,
    )

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',

    )
