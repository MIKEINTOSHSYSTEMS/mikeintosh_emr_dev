# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_
import odoo.modules as addons
loaded_modules = addons.module.loaded
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    allowed_booking_online_days = fields.Integer("Allowed Advance Booking Days", help="No of days for which advance booking is allowed", default=7)
    booking_slot_time = fields.Integer("Minutes in each slot", help="Configure your slot length, 15-30min.", default=15)
    allowed_booking_per_slot = fields.Integer("Allowed Booking per Slot", help="No of allowed booking per slot.", default=4)
    allowed_booking_payment = fields.Boolean("Allowed Advance Booking Payment", help="Allow user to do online Payment")
    yan_appointment_tc = fields.Char('Terms & Conditions Page link', default="/appointment/terms")
    yan_allowed_video_consultation = fields.Boolean("Allowed Online Consultation", help="Allowed Online Consultation")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allowed_booking_online_days = fields.Integer(related='company_id.allowed_booking_online_days',
        string='Allowed Advance Booking Days', readonly=False)
    booking_slot_time = fields.Integer(related='company_id.booking_slot_time',
        string='Minutes in each slot', readonly=False)
    allowed_booking_per_slot = fields.Integer(related='company_id.allowed_booking_per_slot',
        string='Allowed Booking per Slot', readonly=False)

    allowed_booking_payment = fields.Boolean(related='company_id.allowed_booking_payment',
        string='Allowed Advance Booking Payment', readonly=False)
    yan_appointment_tc = fields.Char(related='company_id.yan_appointment_tc',
        string='Terms & Conditions Page link', readonly=False)
    yan_allowed_video_consultation = fields.Boolean(related='company_id.yan_allowed_video_consultation', 
        string="Allowed Online Consultation", help="Allowed Online Consultation", readonly=False)

