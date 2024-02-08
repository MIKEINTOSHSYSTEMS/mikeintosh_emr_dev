# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _yan_get_partner_price(self, quantity=1, uom_id=False, partner=False):
        #if not partner passed use user partner
        if not partner:
            partner = self.env.user.sudo().partner_id

        #check if pricelist is passeed in context or partner has any applied pricelist.
        pricelist_id = False
        yan_pricelist_id = self.env.context.get('yan_pricelist_id')
        if yan_pricelist_id:
            pricelist_id = self.env['product.pricelist'].browse(yan_pricelist_id)
        elif partner.property_product_pricelist:
            pricelist_id = partner.property_product_pricelist

        #if any pricelist pass price based on pricelist else default price.
        if pricelist_id:
            uom = False
            if uom_id:
                uom = self.env['uom.uom'].browse(uom_id)
            price = pricelist_id._get_product_price(self, quantity, uom=uom)
        else:
            price = self.list_price

        return price


class product_template(models.Model):
    _inherit = "product.template"

    form_id = fields.Many2one('drug.form', ondelete='cascade', string='Drug Dose Form', tracking=True)
    active_component_ids = fields.Many2many('active.comp', 'product_active_comp_rel', 'product_id','comp_id','Active Component')
    drug_company_id = fields.Many2one('drug.company', ondelete='cascade', string='Drug Company', help='Company producing this drug')
    hospital_product_type = fields.Selection([
        ('medicament','Medicament'),
        ('fdrinks', 'Food & Drinks'),
        ('os', 'Other Service'),
        ('not_medical', 'Not Medical'),], string="Hospital Product Type", default='medicament')
    indications = fields.Text(string='Indication', help='Indications') 
    therapeutic_effect_ids = fields.Many2many('hms.therapeutic.effect', 'therapeutic_action_rel', 'therapeutic_effect_id', 'effect_id', string='Therapeutic Effect', help='Therapeutic action')
    pregnancy_warning = fields.Boolean(string='Pregnancy Warning',
        help='The drug represents risk to pregnancy')
    lactation_warning = fields.Boolean('Lactation Warning',
        help='The drug represents risk in lactation period')
    pregnancy = fields.Text(string='Pregnancy and Lactancy',
        help='Warnings for Pregnant Women')

    notes = fields.Text(string='Extra Info')
    storage = fields.Char(string='Storage')
    adverse_reaction = fields.Char(string='Adverse Reactions')
    dosage = fields.Float(string='Dosage', help='Dosage')
    product_uom_category_id = fields.Many2one('uom.category', related='uom_id.category_id')
    dosage_uom_id = fields.Many2one('uom.uom', string='Unit of Dosage', domain="[('category_id', '=', product_uom_category_id)]")
    route_id = fields.Many2one('drug.route', ondelete='cascade', 
        string='Route', help='')
    form_id = fields.Many2one('drug.form', ondelete='cascade', 
        string='Form',help='Drug form, such as tablet or gel')


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    product_qty = fields.Float(search="_search_product_qty")

    #canbe used for filtering lots in selection on procedures and consumed products
    def _search_product_qty(self, operator, value):
        valid_record = []
        product_id = self._context.get('yan_product_id',False)
        production_lots = self.search([('product_id','=',product_id)])
        for production_lot in production_lots:
            if operator == '>' and production_lot.product_qty > value:
                valid_record.append(production_lot.id)
        return [('id', 'in', valid_record)]
