from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'
    _description = "The model is inherited into the product.template"

    manufacturer_id = fields.Many2one(
        comodel_name='mobilephones.manufacturer',
        string='Manufacturer',
        ondelete='cascade',
    )

    model_id = fields.Many2one(
        comodel_name='mobilephones.model',
        string='Model',
        domain="[('manufacturer_id', '=', manufacturer_id)]",
    )

    @api.onchange('manufacturer_id')
    def _onchange_manufacturer_id(self):
        if self.model_id and self.model_id.manufacturer_id != self.manufacturer_id:
            self.model_id = None
