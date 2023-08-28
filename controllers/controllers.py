# -*- coding: utf-8 -*-
# from odoo import http


# class LeasMesProcessReporting(http.Controller):
#     @http.route('/leas_mes_process_reporting/leas_mes_process_reporting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/leas_mes_process_reporting/leas_mes_process_reporting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('leas_mes_process_reporting.listing', {
#             'root': '/leas_mes_process_reporting/leas_mes_process_reporting',
#             'objects': http.request.env['leas_mes_process_reporting.leas_mes_process_reporting'].search([]),
#         })

#     @http.route('/leas_mes_process_reporting/leas_mes_process_reporting/objects/<model("leas_mes_process_reporting.leas_mes_process_reporting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('leas_mes_process_reporting.object', {
#             'object': obj
#         })
