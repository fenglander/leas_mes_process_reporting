from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.tools import float_round


class MrpOpenWorkOrderWizard(models.TransientModel):
    _name = 'mrp.open.workorder.wizard'
    _description = 'Open Work Order Reporting Interface Wizard'

    code = fields.Char('Code', required=True)
    workorder_id = fields.Many2one('mrp.workorder')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        return res

    @api.onchange('workorder_id')
    def _onchange_workorder_code(self):
        for rec in self:
            rec.code = rec.workorder_id.code

    def action_launch(self):
        order = self.env['mrp.workorder'].sudo().search([('code', '=', self.code)], limit=1)
        if order:
            return order.action_mrp_workorder_view_form_tablet()
        else:
            raise UserError(_("No Workorder found for the given code. "))

