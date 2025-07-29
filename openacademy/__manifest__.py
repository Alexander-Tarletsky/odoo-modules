{
    'name': 'Open Academy',
    'summary': 'Open Academy module for managing trainings',
 
    'author': 'Alexander Tarletsky',
    'website': 'https://github.com/Alexander-Tarletsky/odoo-modules',
    'license': 'LGPL-3',

    'category': 'Training',
    'version': '18.0.1.0.0',

    'depends': ['base', 'board', 'web', 'mail', 'multi_step_wizard'],

    'data': [
        'security/groups.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'views/courses_views.xml',
        'views/course_price_views.xml',
        'views/sessions_views.xml',
        'views/partner_views.xml',
        'views/add_attendee_wizard.xml',
        'views/sessions_boards.xml',
        'views/course_templates.xml',
        'views/res_config_settings.xml',
        'data/partner_category_data.xml',
        'data/ir_crons.xml',
        'data/session_data.xml',
        'report/session_participants_report.xml',
    ],
    'demo': [
        'demo/partner_demo.xml',
        'demo/courses_demo.xml',
        'demo/sessions_demo.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
