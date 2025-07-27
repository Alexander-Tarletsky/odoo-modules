"""
Set of tests for Create Product Wizard
"""
from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestCreateProductWizard(TransactionCase):
    """
    Test Cases related to CreateProductWizard(`mobilephones.create_product_wizard`)
    """
    def setUp(self, *args, **kwargs):
        super(TestCreateProductWizard, self).setUp()
        self.test_manufacturer_1 = self.env['mobilephones.manufacturer'].create([
            {'name': 'Test Manufacturer 1'}
        ])
        self.test_manufacturer_2 = self.env['mobilephones.manufacturer'].create([
            {'name': 'Test Manufacturer 2'}
        ])
        self.test_model = self.env['mobilephones.model'].create([{
            'title': 'Test Model Phone 1',
            'manufacturer_id': self.test_manufacturer_1.id,
        }])
        self.test_wizard = self.env['mobilephones.create_product_wizard'].create([{
            'categ_id': self.env.ref('product.product_category_all').id}])

    def test_compute_product_name(self):
        self.test_wizard.manufacturer_id = self.test_manufacturer_1.id
        self.test_wizard.model_id = self.test_model.id
        self.assertEqual(
            self.test_wizard.name,
            "Test Manufacturer 1  Test Model Phone 1",
            "Wrong name product",
        )

    def test_state_previous_final(self):

        self.test_wizard.state_previous_final(),
        self.assertEqual(
            self.test_wizard.state,
            "start",
            "Wrong state_previous_final method",
        )

    def test_create_product(self):
        self.test_wizard.manufacturer_id = self.test_manufacturer_1.id
        self.test_wizard.model_id = self.test_model.id
        self.test_wizard.create_product()

        product = self.env['product.product'].search([[
            'name', '=', "Test Manufacturer 1  Test Model Phone 1"
        ]])
        self.assertTrue(
            product,
            "Wrong create product",
        )

    def test_onchange_manufacturer_id(self):
        self.test_wizard.manufacturer_id = self.test_manufacturer_1.id
        self.test_wizard.model_id = self.test_model.id
        self.assertEqual(
            self.test_wizard.model_id.title,
            "Test Model Phone 1",
            "Wrong model_id.name field",
        )

        self.test_wizard.manufacturer_id = None
        self.test_wizard._onchange_manufacturer_id()
        self.assertFalse(
            self.test_wizard.model_id,
            "Wrong model_id.name field",
        )
