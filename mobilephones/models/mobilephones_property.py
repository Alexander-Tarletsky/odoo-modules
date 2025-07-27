from odoo import fields, models


class PropertyModels(models.Model):
    _name = 'mobilephones.property'
    _description = "Mobile Phones models properties"
    _order = 'title'
    _rec_name = 'title'

    active = fields.Boolean(default=True)

    title = fields.Char(string='Properties', required=True)
    description = fields.Char(string='description')
    model_ids = fields.Many2many(
        comodel_name='mobilephones.model',
        string='Models'
    )
