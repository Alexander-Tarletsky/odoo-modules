from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    company_is_open = fields.Boolean(
        string='Is Academy open?',
        default=True,
    )

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user.id,
    )
