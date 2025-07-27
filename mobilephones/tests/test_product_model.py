"""
Set of tests for Product model
"""
from odoo.tests import TransactionCase, tagged, Form


@tagged('-at_install', 'post_install',)
class TestProduct(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestProduct, self).setUp()
        self.test_manufacturer = self.env['mobilephones.manufacturer'].create([
            {'name': 'Test Manufacturer 1'}
        ])
        self.test_model = self.env['mobilephones.model'].create([{
            'title': 'Test Model Phone 1',
            'manufacturer_id': self.test_manufacturer.id,
        }])

    def test_onchange_manufacturer_id(self):
        product_form = Form(self.env['product.template'])
        product_form.categ_id = self.env.ref('product.product_category_all')
        product_form.manufacturer_id = self.test_manufacturer
        product_form.model_id = self.test_model

        self.assertEqual(
            product_form.model_id.title,
            "Test Model Phone 1",
            "Wrong model_id field",
        )

        product_form.manufacturer_id = self.env['mobilephones.manufacturer']
        self.assertFalse(
            product_form.model_id.title,
            "Wrong model_id field",
        )
