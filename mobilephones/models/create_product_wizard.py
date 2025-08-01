from odoo import api, fields, models


class CreateProductWizard(models.TransientModel):
    _name = 'mobilephones.create_product_wizard'
    _description = "Wizard for quick product creation"
    _inherit = ["multi.step.wizard.mixin"]

    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type', default='consu', required=True,
        help='A storable product is a product for which you manage stock.\n'
             'The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')

    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Product Category',
        change_default=True, group_expand='_read_group_categ_id',
        required=True, help="Select category for the current product")

    sale_ok = fields.Boolean('Can be Sold', default=True)
    purchase_ok = fields.Boolean('Can be Purchased', default=True)
    default_code = fields.Char('Internal Reference', index=True)
    image_1920 = fields.Image("Variant Image", max_width=1920, max_height=1920)

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

    name = fields.Char(
        string='Product name',
        compute='_compute_product_name',
        store=True, readonly=True)

    @api.depends('manufacturer_id', 'model_id',)
    def _compute_product_name(self):
        """Compute the product name based on manufacturer and model.

        Combines manufacturer name and model title to create the product name.
        Format: "Manufacturer Model"
        """
        for record in self:
            if record.manufacturer_id and record.model_id:
                record.name = "{}  {}".format(record.manufacturer_id.name, record.model_id.title)

    @api.onchange('manufacturer_id')
    def _onchange_manufacturer_id(self):
        """Handle onchange event when manufacturer is changed.

        Clears the model selection if the selected model doesn't belong
        to the newly selected manufacturer.
        """
        if self.model_id and self.model_id.manufacturer_id != self.manufacturer_id:
            self.model_id = None

    def state_previous_final(self):
        """Set the wizard state back to start.

        Used in multi-step wizard navigation.
        """
        self.state = 'start'

    def create_product(self):
        """Create a new product based on wizard data.

        Creates a product.product record with the values from the wizard form.
        Includes manufacturer and model information.
        """
        args = [{
            'name': self.name,
            'type': self.type,
            'categ_id': self.categ_id.id,
            'purchase_ok': self.purchase_ok,
            'sale_ok': self.sale_ok,
            'default_code': self.default_code,
            'manufacturer_id': self.manufacturer_id.id,
            'model_id': self.model_id.id,
            'image_1920': self.image_1920
        }]
        self.env['product.product'].create(args)
