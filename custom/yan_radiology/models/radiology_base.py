# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class YANLabTestUom(models.Model):
    _name = "yan.radiology.test.uom"
    _description = "Radiology Test UOM"
    _order = 'sequence asc'
    _rec_name = 'code'

    name = fields.Char(string='UOM Name', required=True)
    code = fields.Char(string='Code', required=True, index=True, help="Short name - code for the test UOM")
    sequence = fields.Integer("Sequence", default="100")

    _sql_constraints = [('code_uniq', 'unique (name)', 'The Radiology Test code must be unique')]


class YanRadiology(models.Model):
    _name = 'yan.radiology'
    _description = 'Radiology'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'yan.hms.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }

    description = fields.Text()
    is_collection_center = fields.Boolean('Is Collection Center')
    partner_id = fields.Many2one('res.partner', 'Partner', ondelete='restrict', required=True)
    active = fields.Boolean(string="Active", default=True)


class LabTest(models.Model):
    _name = "yan.radiology.test"
    _description = "Radiology Test Type"
    _rec_names_search = ['name', 'code']

    name = fields.Char(string='Name', help="Test type, eg X-Ray, MRI, Ultrasounds...", index=True)
    code = fields.Char(string='Code', help="Short name - code for the test")
    description = fields.Text(string='Description')
    active = fields.Boolean(string="Active", default=True)
    product_id = fields.Many2one('product.product',string='Service', required=True)
    list_price = fields.Float(related='product_id.list_price', string="Price", readonly=True)
    remark = fields.Char(string='Remark')
    report = fields.Text (string='Test Report')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company' , default=lambda self: self.env.company)
    consumable_line_ids = fields.One2many('hms.consumable.line', 'radiology_test_id',
        string='Consumable Line')
    yan_tat = fields.Char(string='Process Time')
    subsequent_test_ids = fields.Many2many("yan.radiology.test", "yan_radiology_test_rel", "test_id", "sub_test_id", "Subsequent Tests")

    _sql_constraints = [
        ('code_company_uniq', 'unique (code,company_id)', 'The code of the account must be unique per company !')
    ]

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name or ''
            if rec.code:
                name = "%s [%s]" % (rec.name, rec.code)
            res += [(rec.id, name)]
        return res

    def copy(self, default=None):
        self.ensure_one()
        new_name = _('%s (copy)') % self.name
        new_code = _('%s (copy)') % self.code
        default = dict(default or {}, name=new_name, code=new_code)
        return super(LabTest, self).copy(default)


class RadiologyGroupLine(models.Model):
    _name = "radiology.group.line"
    _description = "Radiology Group Line"

    group_id = fields.Many2one('radiology.group', ondelete='restrict', string='Radiology Group')
    test_id = fields.Many2one('yan.radiology.test',string='Test', ondelete='cascade', required=True)
    yan_tat = fields.Char(related='test_id.yan_tat', string='Turnaround Time', readonly=True)
    selected_side = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'), ('both', 'Both')], string='Selected Side')
    radiographic_positioning = fields.Selection([
        ('front', 'Front'),
        ('lateral', 'Lateral'),
        ('back', 'Back')], string='Radiographic Positioning', required=True)
    body_parts = fields.Selection([
        ('abdomen', 'Abdomen'), ('ankle', 'Ankle'), ('arm', 'Arm'), ('arm clavicle', 'Arm Clavicle'),
        ('arm scapula', 'ARM Scapula'), ('arm scaphoid', 'Arm Scaphoid'),
        ('chest', 'Chest'), ('elbow', 'Elbow'), ('foot', 'Foot'),
        ('femur', 'Femur'), ('finger', 'Finger'), ('forearm', 'Forearm'), ('knee', 'Knee'), ('hand', 'Hand'),
        ('head Skull', 'Head Skull'), ('head Mandible', 'Head Mandible'), ('hip', 'Hip'), ('humerus', 'Humerus'),
        ('leg', 'Leg'), ('lumbar', 'Lumbar'),('neck soft', 'Neck soft'), ('pelvis', 'Pelvis'), ('ribs', 'Ribs'),
        ('shoulder', 'Shoulder'), ('spine', 'Spine'), ('wrist', 'Wrist')], string='Body Part', required=True)
    instruction = fields.Char(string='Special Instructions')
    sale_price = fields.Float(string='Sale Price')

    @api.onchange('test_id')
    def onchange_test(self):
        if self.test_id:
            self.sale_price = self.test_id.product_id.lst_price


class RadiologyGroup(models.Model):
    _name = "radiology.group"
    _description = "Radiology Group"

    name = fields.Char(string='Group Name', required=True)
    line_ids = fields.One2many('radiology.group.line', 'group_id', string='Medicament line')

