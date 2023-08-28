# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
import json
from odoo.exceptions import ValidationError
from odoo.modules import module
import logging

_logger = logging.getLogger(__name__)


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    reporting_point = fields.Boolean("Reporting Point", default=True)




