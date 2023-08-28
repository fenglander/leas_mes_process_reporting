# -*- coding: utf-8 -*-
from odoo import models, fields, api
import unicodedata
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

# Deprecated
# class MrpRoutingStation(models.Model):
#     _name = 'mrp.reporting.station'
#     _description = "Production Reporting Station"
#     _inherit = [
#         'mail.thread',
#     ]
#
#     workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True, ondelete="restrict")
#     name = fields.Char('Name', required=True)
#
#     @staticmethod
#     def string_manipulation(text):
#         mapping = {
#             "，": ",", "。": ".", "！": "!", "？": "?", "：": ":", "；": ";", "“": "\"", "”": "\"", "‘": "'", "’": "'",
#             "【": "[", "】": "]", "（": "(", "）": ")", "——": "-", "—": "-", " ": "",
#         }
#         # 全角转半角
#         text = unicodedata.normalize('NFKC', text)
#         # 小写转大写
#         text = text.upper()
#         # 中文转英文
#         for key, value in mapping.items():
#             text = text.replace(key, value)
#         return text
#
#     def create(self, vals_list):
#         # Convert to a List
#         if not isinstance(vals_list, list):
#             vals_list = [vals_list]
#         for vals in vals_list:
#             vals["name"] = self.string_manipulation(vals["name"])
#         return super(MrpRoutingStation, self).create(vals_list)
#
#     @api.constrains('name')
#     def check_reporting_station_name(self):
#         # self.env['mrp.reporting.station'].flush()
#         for station in self:
#             name_count = self.search_count(
#                 [('workcenter_id', '=', station.workcenter_id.id), ('name', '=', station.name)]
#             )
#             if name_count > 1:
#                 raise ValidationError("Ensure the Uniqueness of Names.")
