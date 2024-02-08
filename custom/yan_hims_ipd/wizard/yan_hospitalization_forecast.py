# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta


class YanHospitalizationForecast(models.TransientModel):
    _name = "yan.hospitalization.forecast"
    _description = 'Hospitalization Forecast'
    _rec_name = "hospitalization_id"

    @api.depends('line_ids.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the order.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.company_id.currency_id.round(amount_untaxed),
                'amount_tax': order.company_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    def get_yan_final_due(self):
        for rec in self:
            rec.yan_final_due = rec.yan_amount_due + rec.amount_total

    hospitalization_id = fields.Many2one("yan.hospitalization", string="Hospitalization", readonly=True, required=True)
    patient_id = fields.Many2one("hms.patient", related="hospitalization_id.patient_id", string="Patient", readonly=True, required=True)
    partner_id = fields.Many2one("res.partner", related="hospitalization_id.patient_id.partner_id", string="Partner", readonly=True, required=True)
    date = fields.Datetime("Date", default=fields.Datetime.now())
    line_ids = fields.One2many("yan.hospitalization.forecast.line", 'order_id', string='Forecast Lines', readonly=False, copy=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", related='company_id.currency_id', string="Currency", readonly=True, required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', check_company=True, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    total_invoiced = fields.Monetary(related="patient_id.total_invoiced", string="Total Invoiced")
    yan_amount_due = fields.Monetary(related="patient_id.yan_amount_due", string="Due Amount")
    yan_final_due = fields.Monetary(compute=get_yan_final_due, string="Total Due Amount")


    @api.onchange('hospitalization_id')
    def onchange_hospitalization(self):
        ForecastLine = self.env['yan.hospitalization.forecast.line']
        if self.hospitalization_id:
            fiscal_position_id = self.env['account.fiscal.position']._get_fiscal_position(self.partner_id)
            hospitalization = self.hospitalization_id
            lines = []
            data = hospitalization.yan_hospitalization_invoicing()            
            for product_data in data:
                product = product_data.get('product_id')

                if product:
                    yan_pricelist_id = self.env.context.get('yan_pricelist_id')
                    if not product_data.get('price_unit') and (self.partner_id.property_product_pricelist or yan_pricelist_id):
                        if yan_pricelist_id:
                            pricelist_id = self.env['product.pricelist'].browse(yan_pricelist_id)
                        else:
                            pricelist_id = self.partner_id.property_product_pricelist
                        price = pricelist_id._get_product_price(product, product_data.get('quantity',1.0))
                    else:
                        price = product_data.get('price_unit', product.list_price)
                    
                    tax_ids = product.taxes_id
                    if tax_ids:
                        if fiscal_position_id:
                            tax_ids = fiscal_position_id.map_tax(tax_ids._origin)
                        tax_ids = [(6, 0, tax_ids.ids)]

                    line = ForecastLine.create({
                        'order_id': self.id,
                        'name': product_data.get('name',product.get_product_multiline_description_sale()),
                        'product_id': product.id,
                        'price_unit': price,
                        'product_uom_qty': product_data.get('quantity',1.0),
                        'discount': product_data.get('discount',0.0),
                        'product_uom_id': product_data.get('product_uom_id',product.uom_id.id),
                        'tax_ids': tax_ids,
                    })
                else:
                    line = ForecastLine.create({
                        'order_id': self.id,
                        'name': product_data.get('name'),
                        'display_type': 'line_section',
                    })
                lines.append(line.id)
            self.line_ids = [(6,0,lines)]

    def _get_tax_amount_by_group(self):
        self.ensure_one()
        res = {}
        for line in self.line_ids:
            base_tax = 0
            for tax in line.tax_ids:
                group = tax.tax_group_id
                res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                # FORWARD-PORT UP TO SAAS-17
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = tax.compute_all(price_reduce + base_tax, quantity=line.product_uom_qty,
                                         product=line.product_id, partner=self.create_uid.partner_id)['taxes']
                for t in taxes:
                    res[group]['amount'] += t['amount']
                    res[group]['base'] += t['base']
                if tax.include_base_amount:
                    base_tax += tax.compute_all(price_reduce + base_tax, quantity=1, product=line.product_id,
                                                partner=self.create_uid.partner_id)['taxes'][0]['amount']
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = [(l[0].name, l[1]['amount'], l[1]['base'], len(res)) for l in res]
        return res

    def view_invoices(self):
        invoices = self.env['account.move'].search([('partner_id','=',self.partner_id.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('partner_id', '=', self.partner_id.id)]
        action['context'] = {'search_default_posted': 1, 'search_default_open': 1}
        return action


class YanHospitalizationForecastLine(models.TransientModel):
    _name = 'yan.hospitalization.forecast.line'
    _description = "Forecast Line"
    _order = "sequence, id"

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        """
        Compute the amounts of the line.
        """
        for line in self:
            if not line.display_type:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_ids.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.create_uid.partner_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
            else:
                line.price_tax = 0
                line.price_total = 0
                line.price_subtotal = 0

    order_id = fields.Many2one('yan.hospitalization.forecast', string='Order', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict')
    product_uom_qty = fields.Float(string='Quantity', digits=('Product Unit of Measure'), default=1.0)
    product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    price_unit = fields.Float()
    discount = fields.Float()
    tax_ids = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Taxes Amount', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.company_id.currency_id', store=True, string='Currency', readonly=True)
    display_type = fields.Selection([
        ('line_section', "Section")], help="Technical field for UX purpose.")

