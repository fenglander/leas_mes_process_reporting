# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
import json
from odoo.exceptions import ValidationError
from odoo.modules import module
import logging

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.constrains('operation_ids')
    def check_operations_reporting_point(self):
        self.env['mrp.routing.workcenter'].flush()
        for line in self.operation_ids:
            max_sequence = max(self.env['mrp.routing.workcenter'].search(
                [('bom_id', '=', line.bom_id.id)]).mapped('sequence'))
            if line.sequence == max_sequence and not line.reporting_point:
                raise ValidationError("The last operation must be designated as a reporting point.")
