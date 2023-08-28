from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.tools import float_round


class MrpReportingOpreationnWizard(models.TransientModel):
    _name = 'mrp.reporting.operation.wizard'
    _description = 'Reporting Operation Wizard'

    workorder_id = fields.Many2one('mrp.workorder')
    workcenter_id = fields.Many2one('mrp.workcenter', related='workorder_id.workcenter_id')
    previous_rec = fields.Many2one('mrp.workcenter.productivity', 'Previous Record', readonly=True)
    qty_operation_avail = fields.Float('Available to Start Quantity', related='workorder_id.qty_operation_avail')
    qty_started = fields.Float('Started Quantity')
    qty_completed = fields.Float('Completed Quantity')
    action_type = fields.Selection([('start', 'Start'), ('finish', 'Finish')], 'Action Type')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('active_id'):
            # workorder_id
            workorder_id = self.env.context['active_id']
            res.update({'workorder_id': workorder_id})
            # action_type
            res['action_type'] = self.env.context.get('action_type')
            # qty_started & previous_rec
            domain = [('workorder_id', '=', workorder_id), ('user_id', '=', self.env.user.id)]
            if self.env.context.get('action_type') == 'start':
                domain += [('action_type', 'in', ['block', 'pause']), ('next_rec', '=', False)]
            elif self.env.context.get('action_type') == 'finish':
                domain += [('date_end', '=', False)]

            productivity = self.env['mrp.workcenter.productivity'].sudo().search(domain, limit=1)
            if productivity and productivity.qty_started > 0:
                res['qty_started'] = productivity.qty_started
                res.update({'previous_rec': productivity.id})
            else:
                res['qty_started'] = self.env['mrp.workorder'].sudo().browse(workorder_id).qty_operation_avail
        return res

    def action_launch(self):
        if self.action_type == 'start':
            self.start_action()
        elif self.action_type == 'finish':
            self.finish_action()

    def start_action(self):
        if self.qty_started <= 0:
            raise UserError(_("Required to Fill in the Started Quantity. "))

        elif self.qty_started > self.qty_operation_avail and not self.previous_rec:
            raise UserError(_("Exceeding the Available to Start Quantity. Planned production Quantity: %s, In-Progress "
                              "Quantity: %s, Completed Quantity: %s." % (self.workorder_id.qty_remaining,
                                                                         self.workorder_id.qty_operation_wip,
                                                                         self.workorder_id.qty_operation_comp)))
        qty_started = float_round(self.qty_started, precision_rounding=self.workorder_id.production_id.product_uom_id.rounding)
        self.workorder_id.button_start(qty_started, self.previous_rec)

    def finish_action(self):
        timeline_obj = self.env['mrp.workcenter.productivity']
        comp_items = []
        comp = self.qty_completed if self.qty_completed > 0 else 0
        for workorder in self.workorder_id:
            comp = float_round(comp, precision_rounding=self.workorder_id.production_id.product_uom_id.rounding)
            domain = [('workorder_id', '=', workorder.id), ('date_end', '=', False),
                      ('user_id', '=', self.env.user.id)]
            if comp is not None:
                for timeline in timeline_obj.search(domain, limit=1):
                    if timeline.qty_started >= comp:
                        timeline.qty_completed = comp
                        timeline.action_type = 'finish'
                        qty_wip = workorder.qty_operation_wip - timeline.qty_started
                        workorder.qty_operation_wip = qty_wip if qty_wip > 0 else 0
                        workorder.qty_operation_comp += comp
                    else:
                        raise UserError(_("The completed quantity cannot be greater than the started quantity."))
                    if workorder.qty_remaining > workorder.qty_operation_comp:
                        workorder.end_previous(Part_omp=True)
                    else:
                        workorder.button_finish()
