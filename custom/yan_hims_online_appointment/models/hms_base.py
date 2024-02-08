# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT


def float_to_time(hours):
    """ Convert a number of hours into a time object. """
    if hours == 24.0:
        return time.max
    fractional, integral = math.modf(hours)
    int_fractional = int(float_round(60 * fractional, precision_digits=0))
    if int_fractional > 59:
        integral += 1
        int_fractional = 0
    return time(int(integral), int_fractional, 0)


class Appointment(models.Model):
    _inherit = 'hms.appointment'

    READONLY_CONFIRMED_STATES = {'confirm': [('readonly', True)], 'in_consultation': [('readonly', True)], 'pause': [('readonly', True)], 'to_invoice': [('readonly', True)], 'waiting': [('readonly', True)], 'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    schedule_date = fields.Date(string='Schedule Date', states=READONLY_CONFIRMED_STATES)
    schedule_slot_id = fields.Many2one('appointment.schedule.slot.lines', string = 'Schedule Slot', states=READONLY_CONFIRMED_STATES)
    booked_online = fields.Boolean('Booked Online', states=READONLY_CONFIRMED_STATES)

    @api.model
    def clear_appointment_cron(self):
        if self.env.user.company_id.allowed_booking_payment:
            appointments = self.search([('booked_online','=', True),('state','=','draft')])
            for appointment in appointments:
                #cancel appointment after 20 minute if not paid
                create_time = appointment.create_date + timedelta(minutes=20)
                if create_time <= datetime.now():
                    if appointment.invoice_id:
                        if appointment.invoice_id.state=='paid':
                            continue
                        appointment.invoice_id.action_invoice_cancel()
                    appointment.appointment_cancel()

    #To Avoid code duplication in mobile api.
    def yan_get_slot_lines(self, physician_id, department_id, date, schedule_type):
        if date:
            domain = [('slot_id.slot_date','=', date),('from_slot','>=',fields.Datetime.now()),('rem_limit','>=',1)]
        else:
            last_date = fields.Date.today() + timedelta(days=self.env.user.sudo().company_id.allowed_booking_online_days)
            domain = [('rem_limit','>=',1),('from_slot','>=',fields.Datetime.now()),('slot_id.slot_date','<=',last_date)]

        if physician_id:
            domain += [('physician_id', '=', int(physician_id))]
        if department_id:
            domain += [('department_id', '=', int(department_id))]

        domain += [('slot_id.schedule_id.schedule_type', '=', schedule_type)]
        slot_lines = self.env['appointment.schedule.slot.lines'].sudo().search(domain)
        return slot_lines

    def get_slot_data(self, physician_id, department_id, date=False, schedule_type="appointment"):
        slot_lines = self.yan_get_slot_lines(physician_id, department_id, date, schedule_type)
        slot_data = []
        for slot in slot_lines:
            slot_data.append({
                'date': slot.slot_id.slot_date,
                'name': slot.name,
                'id': slot.id,
                'physician_id': slot.physician_id.id,
                'physician_name': slot.physician_id and slot.physician_id.name or '',
                'fees': slot.appointment_price,
                'show_fees': slot.slot_id.schedule_id.show_fee_on_booking,
            })
        return slot_data

    def get_disabled_dates(self, physician_id, department_id, date=False, schedule_type="appointment"):
        slot_lines = self.yan_get_slot_lines(physician_id, department_id, date, schedule_type)
        dates = slot_lines.mapped('slot_id.slot_date')
        available_dates = []
        for av_date in dates:
            available_dates.append(fields.Date.to_string(av_date))

        disabled_dates = []
        start_date = fields.Date.today()
        if date and slot_lines:
            return []
        for days in range(0, self.env.user.sudo().company_id.allowed_booking_online_days + 1):
            date = fields.Date.to_string(fields.Date.today() + timedelta(days=days))
            if date not in available_dates:
                disabled_dates.append(date)
        return disabled_dates

    @api.onchange('schedule_slot_id')
    def onchange_schedule_slot_id(self):
        if self.schedule_slot_id:
            self.date = self.schedule_slot_id.from_slot
            self.date_to = self.schedule_slot_id.to_slot

    @api.onchange('schedule_date')
    def onchange_schedule_date(self):
        if self.schedule_date and self.schedule_slot_id and self.schedule_date!=self.schedule_slot_id.slot_id.slot_date:
            self.schedule_slot_id = False

    def _get_default_payment_link_values(self):
        self.ensure_one()
        product_data = self.yan_appointment_inv_product_data()
        amount = self.yan_get_total_amount(product_data, self.patient_id.partner_id)
        return {
            'description': self.name or _('Appointment Payment'),
            'amount': amount,
            'currency_id': self.company_id.currency_id.id,
            'partner_id': self.patient_id.partner_id.id,
            'amount_max': amount
        }

    def yan_get_total_amount(self, product_data, partner):
        total_amount = 0
        for data in product_data:
            product = data.get('product_id')
            if product:
                yan_pricelist_id = self.env.context.get('yan_pricelist_id')
                if not data.get('price_unit') and (partner.property_product_pricelist or yan_pricelist_id):
                    if yan_pricelist_id:
                        pricelist_id = self.env['product.pricelist'].browse(yan_pricelist_id)
                    else:
                        pricelist_id = partner.property_product_pricelist
                    price = pricelist_id._get_product_price(product, data.get('quantity',1.0))
                else:
                    price = data.get('price_unit', product.list_price)
                total_amount += price * data.get('quantity',1.0)
        return total_amount


class HrDepartment(models.Model):
    _inherit = "hr.department"

    allowed_online_booking = fields.Boolean("Allowed Online Booking")
    basic_info = fields.Char("Basic Info", help="Publish on Website")
    image = fields.Binary(string='Image')
    allow_home_appointment = fields.Boolean("Allowed Home Visit Booking")
    show_fee_on_booking = fields.Boolean("Show Fees")


class HmsPhysician(models.Model):
    _inherit = "hms.physician"

    allowed_online_booking = fields.Boolean("Allowed Online Booking")
    basic_info = fields.Char("Basic Info", help="Publish on Website")
    allow_home_appointment = fields.Boolean("Allowed Home Visit Booking")
    show_fee_on_booking = fields.Boolean("Show Fees")


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    yan_appointment_id = fields.Many2one("hms.appointment", string="Appointment")

    #Update Payments directs after successful payment.
    def _reconcile_after_done(self):
        for tx in self.filtered(lambda t: t.operation != 'validation' and t.yan_appointment_id):
            tx._yan_update_apppointment()
        return super(PaymentTransaction, self)._reconcile_after_done()

    #Update appointment data.
    def _yan_update_apppointment(self):
        self.ensure_one()
        self.yan_appointment_id.sudo().with_context(yan_online_transaction=True,default_create_stock_moves=False).create_invoice()
        if self.yan_appointment_id.sudo().state!='confirm':
            self.yan_appointment_id.sudo().with_context(yan_online_transaction=True).appointment_confirm()

        # Setup access token in advance to avoid serialization failure between
        # edi postprocessing of invoice and displaying the sale order on the portal
        self.yan_appointment_id.invoice_id._portal_ensure_token()
        self.invoice_ids = [(6, 0, [self.yan_appointment_id.invoice_id.id])]

