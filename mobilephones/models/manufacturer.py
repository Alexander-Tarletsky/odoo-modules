from odoo import fields, models


class Manufacturer(models.Model):
    _name = 'mobilephones.manufacturer'
    _description = "Mobile Phones Manufacturer"
    _order = 'name'
    _rec_name = 'name'

    active = fields.Boolean(default=True)

    name = fields.Char(string='Manufacturer', required=True)
    description = fields.Char(string='description')
    model_ids = fields.One2many(
        comodel_name='mobilephones.model',
        inverse_name='manufacturer_id',
        string='Models'
    )
