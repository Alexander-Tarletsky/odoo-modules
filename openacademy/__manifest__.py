{
    'name': "Open Academy",
    'summary': "Open Academy module for managing trainings",

    'author': "Alexander Tarletsky",
    'website': "https://ventor.tech/",

    'category': 'Test',
    'version': '14.0.0.9.0',

    'depends': ['base', 'board', 'web', 'mail'],

    'data': [
        'security/groups.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'views/courses_views.xml',
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
