# coding: utf-8

from odoo import models, api, fields
from datetime import date, datetime, timedelta


class YanRescheduleAppointments(models.TransientModel):
    _name = 'yan.reschedule.appointments'
    _description = "Reschedule Appointments"

    yan_reschedule_time = fields.Float(string="Reschedule Selected Appointments by (Hours)", required=True)

    def yan_reschedule_appointments(self):
        appointments = self.env['hms.appointment'].search([('id','in',self.env.context.get('active_ids'))])
        #YAN: do it in method only to use that method for notifications.
        appointments.yan_reschedule_appointments(self.yan_reschedule_time)
