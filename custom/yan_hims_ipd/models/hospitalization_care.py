# coding=utf-8

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
import dateutil.relativedelta
from odoo.exceptions import ValidationError, AccessError, UserError, RedirectWarning, Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AdmissionCheckListTemplate(models.Model):
    _name="inpatient.checklist.template"
    _description = "Inpatient Checklist Template"

    name = fields.Char(string="Name", required=True)
    remark = fields.Char(string="Remarks")


class AdmissionCheckList(models.Model):
    _name="inpatient.checklist"
    _description = "Inpatient Checklist"

    name = fields.Char(string="Name", required=True)
    is_done = fields.Boolean(string="Y/N")
    remark = fields.Char(string="Remarks")
    hospitalization_id = fields.Many2one("yan.hospitalization", ondelete="cascade", string="Hospitalization")


class PreWardCheckListTemplate(models.Model):
    _name="pre.ward.check.list.template"
    _description = "Pre Ward Checklist Template"

    name = fields.Char(string="Name", required=True)
    remark = fields.Char(string="Remarks")


class PreWardCheckList(models.Model):
    _name="pre.ward.check.list"
    _description = "Pre Ward Checklist"

    name = fields.Char(string="Name", required=True)
    is_done = fields.Boolean(string="Done")
    remark = fields.Char(string="Remarks")
    hospitalization_id = fields.Many2one("yan.hospitalization", ondelete="cascade", string="Hospitalization")


class PatientAccommodationHistory(models.Model):
    _name = "patient.accommodation.history"
    _rec_name = "patient_id"
    _description = "Patient Accommodation History"

    def _rest_time(self):
        for registration in self:
            rest_time = 0
            end_date = registration.end_date or fields.Datetime.now()
            if end_date and registration.start_date:
                diff = end_date - registration.start_date
                if registration.bed_id.invoice_policy=='full':
                    rest_time = diff.days if diff.days > 0 else 1
                else:
                    total_seconds = int(diff.total_seconds())
                    rest_time = (total_seconds/3600) if total_seconds else 0
            registration.rest_time = rest_time

    @api.depends('account_move_line_ids')
    def yan_get_move_lines_data(self):
        for rec in self:
            rec.invoiced_rest_time = sum(rec.account_move_line_ids.mapped('quantity'))

    hospitalization_id = fields.Many2one('yan.hospitalization', ondelete="cascade", string='Inpatient')
    patient_id = fields.Many2one('hms.patient', ondelete="restrict", string='Patient', required=True)
    ward_id = fields.Many2one('hospital.ward', ondelete="restrict", string='Ward/Room')
    bed_id = fields.Many2one('hospital.bed', ondelete="restrict", string='Bed No.')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    rest_time = fields.Float(compute=_rest_time, string='Rest Time')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', related='hospitalization_id.company_id') 
    invoice_policy = fields.Selection(related="bed_id.invoice_policy", string='Invoice Policy', readonly=True)
    account_move_line_ids = fields.Many2many('account.move.line', 'yan_accomodation_account_move_line_rel', 'move_id', 'accommodation_id', string='Invoice Lines')
    invoiced_rest_time = fields.Float(compute="yan_get_move_lines_data", string="Invoiced Rest Time")


class WardRounds(models.Model):
    _name = "ward.rounds"
    _description = "Ward Rounds"

    instruction = fields.Char(string='Instruction')
    remarks = fields.Char(string='Remarks')
    hospitalization_id = fields.Many2one('yan.hospitalization', ondelete="restrict",string='Inpatient')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    physician_id = fields.Many2one('hms.physician', string='Physician', ondelete="restrict")
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)


class YANCarePlanTemplate(models.Model):
    _name = "hms.care.plan.template"
    _description = "Care Plan Template"

    name= fields.Char(string='Care Plan Name')
    diseases_id = fields.Many2one ('hms.diseases', ondelete='restrict', string='Disease')
    nursing_plan = fields.Text (string='Nursing Plan')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: