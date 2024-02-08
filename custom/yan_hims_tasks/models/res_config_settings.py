# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    patient_registration_product_id = fields.Many2one('product.product', 
        related='company_id.patient_registration_product_id',
        domain=[('type','=','service')],
        string='Patient Registration Invoice Product', 
        ondelete='cascade', help='Registration Product', readonly=False)
    treatment_registration_product_id = fields.Many2one('product.product', 
        related='company_id.treatment_registration_product_id',
        domain=[('type','=','service')],
        string='Treatment Registration Invoice Product', 
        ondelete='cascade', help='Registration Product', readonly=False)
    consultation_product_id = fields.Many2one('product.product', 
        related='company_id.consultation_product_id',
        domain=[('type','=','service')],
        string='Consultation Invoice Product', 
        ondelete='cascade', help='Consultation Product', readonly=False)
    followup_days = fields.Float(related='company_id.followup_days', string='Followup Days', readonly=False)
    followup_product_id = fields.Many2one('product.product', 
        related='company_id.followup_product_id',
        domain=[('type','=','service')],
        string='Follow-up Invoice Product', 
        ondelete='cascade', help='Followup Product', readonly=False)
    yan_followup_activity_type_id = fields.Many2one('mail.activity.type', 
        related='company_id.yan_followup_activity_type_id',
        string='Follow-up Activity Type', 
        ondelete='cascade', help='Followup Activity Type', readonly=False)
    registration_date = fields.Char(related='company_id.registration_date', string='Date of Registration', readonly=False)
    appointment_invoice_policy = fields.Selection(related='company_id.appointment_invoice_policy', string="Appointment Invoicing Policy", readonly=False)
    yan_check_appo_payment = fields.Boolean(related='company_id.yan_check_appo_payment', string="Check Appointment Payment Status before Accepting Request", readonly=False)
    yan_appointment_planned_duration = fields.Float(related='company_id.yan_appointment_planned_duration', 
        string='Default Appointment Planned Duration', readonly=False)
    appointment_usage_location_id = fields.Many2one('stock.location', 
        related='company_id.appointment_usage_location_id',
        domain=[('usage','=','customer')],
        string='Usage Location for Consumed Products in Appointment', readonly=False)
    appointment_stock_location_id = fields.Many2one('stock.location', 
        related='company_id.appointment_stock_location_id',
        domain=[('usage','=','internal')],
        string='Stock Location for Consumed Products in Appointment', readonly=False)

    procedure_usage_location_id = fields.Many2one('stock.location', 
        related='company_id.procedure_usage_location_id',
        domain=[('usage','=','customer')],
        string='Usage Location for Consumed Products in Procedure', readonly=False)
    procedure_stock_location_id = fields.Many2one('stock.location', 
        related='company_id.procedure_stock_location_id',
        domain=[('usage','=','internal')],
        string='Stock Location for Consumed Products in Procedure', readonly=False)

    group_patient_registartion_invoicing = fields.Boolean("Patient Registration Invoicing", implied_group='yan_hims_tasks.group_patient_registartion_invoicing')
    group_treatment_invoicing = fields.Boolean("Treatment Invoicing", implied_group='yan_hims_tasks.group_treatment_invoicing')
    yan_prescription_qrcode = fields.Boolean(related='company_id.yan_prescription_qrcode', string="Print Authetication QrCode on Presctiprion", readonly=False)
    auto_followup_days = fields.Float(related='company_id.auto_followup_days', string='Default Followup on (Days)', readonly=False)
    patient_weight_measure_uom = fields.Char(string='Patient Weight unit of measure', config_parameter='yan_hims_tasks.yan_patient_weight_uom')
    patient_height_measure_uom = fields.Char(string='Patient Height unit of measure', config_parameter='yan_hims_tasks.yan_patient_height_uom')
    patient_temp_measure_uom = fields.Char(string='Patient Temp unit of measure', config_parameter='yan_hims_tasks.yan_patient_temp_uom')
    patient_spo2_measure_uom = fields.Char(string='Patient SpO2 unit of measure', config_parameter='yan_hims_tasks.yan_patient_spo2_uom')
    patient_rbs_measure_uom = fields.Char(string='Patient RBS unit of measure', config_parameter='yan_hims_tasks.yan_patient_rbs_uom')
    patient_head_circum_measure_uom = fields.Char(string='Patient Head Circumference unit of measure', config_parameter='yan_hims_tasks.yan_patient_head_circum_uom')
    cancel_old_appointment = fields.Boolean(string='Cancel Old Appointment', config_parameter='yan_hims_tasks.cancel_old_appointment')
    yan_auto_appo_confirmation_mail = fields.Boolean(string="Send Appointment Confirmation Mail", 
        related='company_id.yan_auto_appo_confirmation_mail', readonly=False)

    yan_reminder_day = fields.Float(related='company_id.yan_reminder_day',string="Reminder Days", readonly=False)
    yan_reminder_hours = fields.Float(related='company_id.yan_reminder_hours',string="Reminder Hours", readonly=False)
    yan_flag_days = fields.Integer(related='company_id.yan_flag_days', string="Warning Flag Days", help="Days to count cancelled appointment", readonly=False)
    yan_flag_count_limit = fields.Integer(related='company_id.yan_flag_count_limit', string="Count Limit for Flag", help="Configure number to show alert flag after couting that many cancelled appoitments", readonly=False)
