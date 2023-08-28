# -*- coding: utf-8 -*-
{
    'name': "MES Process Reporting",

    'summary': """
        In the management of operation reporting, it is crucial to accurately record the start and end time of each 
        operation, as well as the quantity processed at each station, in order to reflect the real production capacity.
         Additionally, it is important to control the production process to ensure that products are manufactured 
         according to the defined process. This ensures the accuracy and efficiency of the production process.""",

    'description': """
        
    """,

    'author': "Leas",
    'website': "http://www.leas.life",

    # for the full list
    'category': 'MES',
    'version': '15.0.0.0',
    'category': 'Manufacturing',
    'license': 'OPL-1',
    # any module necessary for this one to work correctly
    'images': [
        'static/description/cover1.png',
        'static/description/Demo1.gif',
        'static/description/Demo2.gif',
        'static/description/Demo3.gif',
        'static/description/Demo4.gif',
        'static/description/Demo5.png',
        'static/description/Demo6.png',
    ],
    'depends': ['base', 'mrp', 'leas_chart_widget'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_routing_workcenter.xml',
        'views/mrp_workcenter.xml',
        'views/mrp_bom.xml',
        'views/mrp_workorder.xml',
        'views/mrp_reporting_operation_wizard.xml',
        'views/mrp_open_workorder_wizard.xml',
        'views/mrp_workcenter_productivity.xml',
        'data/mrp_workorder_seq.xml',
    ],
    # only loaded in demonstration mode
    'assets': {
        'web.assets_backend': [
            'leas_mes_process_reporting/static/src/scss/tablet.scss',
            'leas_mes_process_reporting/static/src/js/workorder_tablet.js',
        ],
    },
    'installable': True,
    'application': True,
}
