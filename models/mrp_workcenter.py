# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
import json
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


def get_daily_eff_chart_json(dates_efficiency):
    color = ["#F45B69", "#91CC75"]
    legend_data = [_('Duration'), _('Efficiency'), ]
    efficiency = []
    duration = []
    xAxis_data = []
    for item in dates_efficiency:
        xAxis_data.append(item["date"])
        duration.append(item["duration"])
        efficiency.append(item["efficiency"])

    data = {
        "backgroundColor": "",
        "textStyle": {"color": '#ffffff'},
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "cross"
            }
        },
        "grid": {
            "right": "10%",
            "left": "5%"
        },
        "toolbox": {
            "feature": {
                "dataView": {"show": True, "readOnly": False},
                "restore": {"show": True},
                "saveAsImage": {"show": True}
            }
        },
        "legend": {
            "textStyle": {"color": '#ffffff'},
            "data": legend_data
        },
        "xAxis": [
            {
                "type": "category",
                "axisTick": {"alignWithLabel": True},
                "data": xAxis_data,
            }
        ],
        "yAxis": [
            {
                "type": "value",
                "name": legend_data[0],
                "position": "right",
                "alignTicks": True,
                "splitLine": {"show": False},
                "axisLine": {"show": True, "lineStyle": {"color": color[0]}},
                "axisLabel": {"formatter": "{value} hours"}
            },
            {
                "type": "value",
                "name": legend_data[1],
                "position": "left",
                "alignTicks": True,
                "splitLine": {"show": False},
                # "offset": 80,
                "axisLine": {"show": True, "lineStyle": {"color": color[1]}},
                "axisLabel": {"formatter": "{value} %"}
            },
        ],
        "series": []
    }
    data["series"].append({"name": legend_data[0], "type": "bar", "data": duration, "color": color[0]})
    data["series"].append({"name": legend_data[1], "type": "line", "yAxisIndex": 1, "data": efficiency, "color": color[1]})

    return data


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    thirty_daily_efficiency = fields.Char('Monthly Daily Efficiency', compute='_compute_thirty_daily_efficiency')

    @api.depends('time_ids')
    def _compute_thirty_daily_efficiency(self):
        today = datetime.today()
        thirty_days_ago = (today - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        for workcenter in self:
            time_log = self.env['mrp.workcenter.productivity'].search([
                ('workcenter_id', '=', workcenter.id),
                ('date_start', '>=', thirty_days_ago)
            ])

            if time_log:
                dates_efficiency = time_log.calc_dates_efficiency()
                chart_json = get_daily_eff_chart_json(dates_efficiency)
                workcenter.thirty_daily_efficiency = json.dumps(chart_json, indent=4)

    def calculate_daily_efficiency(self, product_times, product_outputs, dates):
        daily_efficiency = []
        for day in range(len(dates)):
            total_work_time = 0
            planned_work_time = 0

            for product in product_times:
                wo = self.env['mrp.workorder'].browse(int(product))
                total_work_time += product_times[product][day] * product_outputs[product][day]
                planned_work_time += product_outputs[product][day] * wo.duration_expected / wo.qty_production

            if total_work_time > 0:
                efficiency = (planned_work_time / total_work_time) * 100
                daily_efficiency.append({'date': dates[day].strftime("%Y-%m-%d"), 'efficiency': round(efficiency, 2)})
            else:
                daily_efficiency.append({'date': dates[day].strftime("%Y-%m-%d"), 'efficiency': 0})
        return daily_efficiency

    def get_worksheet_duration(self, dates):
        res = []
        attendance_obj = self.env['resource.calendar.attendance'].sudo()
        for date in dates:
            if not isinstance(date, datetime):
                date = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = date.weekday()
            domain = [('dayofweek', '=', day_of_week), ('id', 'in', self.resource_calendar_id.attendance_ids.ids)]
            if self.resource_calendar_id.two_weeks_calendar:
                week_type = attendance_obj.get_week_type(date)
                domain += [('week_type', '=', week_type)]
            attendances = attendance_obj.search(domain)
            hour_count = 0.0
            for attendance in attendances:
                hour_count += attendance.hour_to - attendance.hour_from
            res.append(hour_count)
        return res


class MrpProductionWorkcenterLineTime(models.Model):
    _inherit = 'mrp.workcenter.productivity'
