from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_is_open = fields.Boolean(
        related='company_id.company_is_open',
        readonly=False,
    )

    default_responsible_id = fields.Many2one(
        string='Default Responsible',
        related='company_id.responsible_id',
        default_model='openacademy.course',
        readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
