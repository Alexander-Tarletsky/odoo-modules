from odoo import fields, models


class _Model(models.Model):
    _name = 'mobilephones.model'
    _description = "Mobile Phones Model"
    _order = 'title'
    _rec_name = 'title'

    active = fields.Boolean(default=True)

    title = fields.Char(string='Model', required=True)
    description = fields.Char(string='description')

    manufacturer_id = fields.Many2one(
        comodel_name='mobilephones.manufacturer',
        string='Manufacturer',
        ondelete='cascade',
        required=True,
    )
    property_ids = fields.Many2many(
        comodel_name='mobilephones.property',
        string='Properties'
    )
