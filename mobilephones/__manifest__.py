{
    'name': "Mobile Phones",
    'summary': "Mobile Phones module for managing trainings",

    'author': "Alexander Tarletsky",
    'website': "https://ventor.tech/",

    'category': 'Test',
    'version': '14.0.0.1.0',

    'depends': ['base', 'mail', 'sale', 'multi_step_wizard'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/manufacturer_view.xml',
        'views/model_view.xml',
        'views/property_view.xml',
        'views/create_product_wizard.xml',
    ],
    'demo': [
        'demo/manufacturer_demo.xml',
        'demo/property_demo.xml',
        'demo/model_demo.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
