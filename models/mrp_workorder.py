# -*- coding: utf-8 -*-
import ast

from odoo import models, fields, _, api
import json
import os
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    # Used to create input fields in the interface to facilitate user input of information.

    code = fields.Char('Code', readonly=True)
    reporting_point = fields.Boolean(related='operation_id.reporting_point', default=True, store=True)
    qty_operation_wip = fields.Float('In-Process Quantity')
    qty_operation_comp = fields.Float('Completed Quantity')
    qty_operation_avail = fields.Float('Available Quantity', compute='_compute_qty_operation_avail')
    wo_Proc_chart_data = fields.Char('Workorder Process', compute='_compute_Proc_chart_data')
    mo_Proc_chart_data = fields.Char('production Process', compute='_compute_Proc_chart_data')
    workorder_efficiency = fields.Float('Workorder Efficiency', compute='_compute_workorder_efficiency')
    thirty_daily_efficiency = fields.Char(related='workcenter_id.thirty_daily_efficiency')

    def button_start(self, qty_started=None, previous_rec=None):
        self.ensure_one()
        # 判断可开工数量 （计划开工-生产中-已完工） qty_remaining 计划生产数量 qty_operation_wip 生产中 qty_operation_comp 已完工
        if self.qty_operation_avail <= 0 and self.qty_operation_wip <= 0:
            raise UserError(_("No Available to Start Quantity. Planned production Quantity: %s, In-Progress "
                              "Quantity: %s, Completed Quantity: %s." % (self.query_comp_qty(),
                                                                         self.qty_operation_wip,
                                                                         self.qty_operation_comp)))
        super().button_start()
        if qty_started is not None:
            qty_wip = self.qty_operation_wip + (0 if previous_rec else qty_started)
            self.qty_operation_wip = qty_wip if qty_wip <= self.qty_remaining else self.qty_remaining
            domain = [('workorder_id', '=', self.id), ('date_end', '=', False),
                      ('user_id', '=', self.env.user.id)]
            productivity = self.env['mrp.workcenter.productivity'].search(domain, limit=1, order='date_start ASC')
            productivity.qty_started = qty_started
            if previous_rec is not None or previous_rec:
                previous_rec.next_rec = productivity.id

    def end_previous(self, doall=False, Part_omp=False):
        """
        Args:
            doall: inherit
            Part_omp: Indicates that the current reporting is completed, and there are no further tasks. Otherwise,
            it will be marked as paused, and when the next operation starts, the last end information will be read
            to record continuous working time information.
        Returns:

        """
        if not Part_omp:
            timeline_obj = self.env['mrp.workcenter.productivity']
            domain = [('workorder_id', 'in', self.ids), ('date_end', '=', False)]
            if not doall:
                domain.append(('user_id', '=', self.env.user.id))
            for timeline in timeline_obj.search(domain, limit=None if doall else 1):
                if doall:
                    timeline.action_type = 'block'
                else:
                    timeline.action_type = 'pause'
        super().end_previous(doall)

    def button_reporting_start(self):
        self.ensure_one()
        return self.open_reporting_wizard(action_type='start')

    def button_reporting_finish(self):
        self.ensure_one()
        return self.open_reporting_wizard(action_type='finish')

    def open_reporting_wizard(self, action_type):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Operation ' + action_type),
            'res_model': 'mrp.reporting.operation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id,
                        'action_type': action_type},
            'views': [[False, 'form']]
        }

    def open_workorder_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Open Workorder Reporting Interface'),
            'res_model': 'mrp.open.workorder.wizard',
            'view_mode': 'form',
            'target': 'new',
            'views': [[False, 'form']]
        }

    def action_mrp_workorder_view_form_tablet(self):
        view_id = self.env.ref('leas_mes_process_reporting.mrp_workorder_view_form_tablet').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Operation Reporting'),
            'res_model': 'mrp.workorder',
            'target': 'fullscreen',
            'res_id': self.id,
            'views': [[view_id, 'form']],
            'view_id': view_id,
            'flags': {
                'withControlPanel': False,
                'form_view_initial_mode': 'edit',
            },
        }

    def _start_nextworkorder(self):
        super()._start_nextworkorder()
        is_first = self.env['mrp.workorder'].sudo().search([('next_work_order_id', '=', self.id)])
        if self.qty_operation_comp == 0 and is_first:
            return
        next_order = self.next_work_order_id
        parallel_orders = []
        while next_order and not next_order.reporting_point:
            parallel_orders.append(next_order)
            next_order = next_order.next_work_order_id
        parallel_orders.append(next_order)
        for order in parallel_orders:
            if order.state == 'pending' and order.qty_operation_avail > 0:
                order.state = 'ready' if order.production_availability == 'assigned' else 'waiting'

    @api.constrains('qty_operation_wip', 'qty_operation_comp')
    def _check_qty_operation(self):
        for wo in self:
            if wo.state in ['done', 'cancel']:
                raise UserError(_(u"Not allowed to modify the completion quantity of completed work orders."))
            ref_qty = wo.query_comp_qty()
            if wo.qty_operation_wip > ref_qty or wo.qty_operation_comp > ref_qty or \
                    wo.qty_operation_wip > (ref_qty - wo.qty_operation_comp):
                raise UserError(_(u"Cannot Exceed Work Order Quantity."))
            if wo.qty_operation_wip < 0 or wo.qty_operation_comp < 0:
                raise UserError(_(u"Not Support Negative Numbers."))
            par_orders = self.browse()
            next_order = wo.next_work_order_id
            if not wo.reporting_point:
                continue
            while next_order and not next_order.reporting_point:
                par_orders |= next_order
                next_order = next_order.next_work_order_id
            par_orders |= next_order
            max_par_op_qty = max(x.qty_operation_wip + x.qty_operation_comp for x in par_orders)
            if wo.qty_operation_comp < max_par_op_qty:
                raise UserError(_(u"Subsequent operations have started, and the completion quantity "
                                  u"cannot be lower than %s." % str(max_par_op_qty)))

    @api.model
    def create(self, values):
        values['code'] = self.env['ir.sequence'].next_by_code('mrp.workorder') or '/'
        res = super().create(values)
        return res

    def action_return_view_workorder(self):
        '''
        Return to List View
        '''
        action = self.env['ir.actions.act_window']._for_xml_id('mrp.mrp_workorder_todo')
        context = dict(self.env.context)
        action_context = ast.literal_eval(action['context'])
        context.update(action_context)
        action['context'] = context
        action['target'] = 'main'

        return action

    @api.depends('qty_remaining', 'qty_operation_wip', 'qty_operation_comp')
    def _compute_Proc_chart_data(self):
        name_qty_operation_wip = self._fields['qty_operation_wip'].string
        name_qty_operation_comp = self._fields['qty_operation_comp'].string
        name_qty_operation_avail = self._fields['qty_operation_avail'].string
        for rec in self:
            chart_data = []
            for wo in rec.production_id.workorder_ids:
                chart_data.append({'category': wo.name,
                                   name_qty_operation_avail: wo.qty_operation_avail,
                                   name_qty_operation_wip: wo.qty_operation_wip,
                                   name_qty_operation_comp: wo.qty_operation_comp})
            rec.mo_Proc_chart_data = json.dumps(chart_data, indent=4)
            chart_data = [
                {'value': rec.qty_operation_avail, 'name': name_qty_operation_avail},
                {'value': rec.qty_operation_wip, 'name': name_qty_operation_wip},
                {'value': rec.qty_operation_comp, 'name': name_qty_operation_comp},
            ]
            rec.wo_Proc_chart_data = json.dumps(chart_data, indent=4)

    @api.depends('time_ids')
    def _compute_workorder_efficiency(self):
        for wo in self:
            planned_proc_time = wo.duration_expected / wo.qty_production
            done_times = [time for time in wo.time_ids if time.action_type == 'finish']
            comp_qty = 0
            comp_duration = 0
            for time in done_times:
                comp_qty = comp_qty + time.qty_completed
                proc_records = time.get_processing_time_recs()
                comp_duration += sum(proc_records.mapped('duration'))
            if comp_duration:
                wo.workorder_efficiency = round(comp_qty * planned_proc_time / comp_duration * 100, 2)
            else:
                wo.workorder_efficiency = 0

    @api.depends('time_ids')
    def _compute_workorder_efficiency(self):
        for wo in self:
            planned_proc_time = wo.duration_expected / wo.qty_production
            done_times = [time for time in wo.time_ids if time.action_type == 'finish']
            comp_qty = 0
            comp_duration = 0
            for time in done_times:
                comp_qty = comp_qty + time.qty_completed
                proc_records = time.get_processing_time_recs()
                comp_duration += sum(proc_records.mapped('duration'))
            if comp_duration:
                wo.workorder_efficiency = round(comp_qty * planned_proc_time / comp_duration * 100, 2)
            else:
                wo.workorder_efficiency = 0

    @api.depends('qty_remaining', 'qty_operation_wip', 'qty_operation_comp')
    def _compute_qty_operation_avail(self):
        for rec in self:
            prev_comp_qty = rec.query_comp_qty()
            rec.qty_operation_avail = prev_comp_qty - rec.qty_operation_wip - rec.qty_operation_comp

    def query_comp_qty(self):
        self.ensure_one()
        prev_rec = self.search([('next_work_order_id', '=', self.id)], limit=1)
        if prev_rec:
            if prev_rec.reporting_point:
                return prev_rec.qty_operation_comp
            else:
                return prev_rec.query_comp_qty()
        else:
            if self.state == 'done':
                return self.qty_operation_comp
            else:
                return self.qty_produced or self.qty_producing or self.qty_production
