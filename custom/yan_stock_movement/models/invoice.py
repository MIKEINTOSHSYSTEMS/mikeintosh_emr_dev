# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResUsers(models.Model):
    _inherit = "res.users"

    yan_warehouse_id = fields.Many2one('stock.warehouse', 'Default Picking Warehouse', copy=False)
    yan_picking_type_id = fields.Many2one('stock.picking.type', 'Default Picking Type', copy=False)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['yan_warehouse_id', 'yan_picking_type_id']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['yan_warehouse_id', 'yan_picking_type_id']


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    yan_account_move_line_id = fields.Many2one('account.move.line', help="Technical field to set lot properly for auto picking.")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tracking = fields.Selection(related='product_id.tracking', store=True)
    yan_lot_id = fields.Many2one("stock.lot", string="Batch Number",
        domain="[('product_id', '=', product_id),('product_qty','>',0),'|',('expiration_date','=',False),('expiration_date', '>', context_today().strftime('%Y-%m-%d'))]")
    exp_date = fields.Datetime(string="Expiry Date")
    
    @api.onchange('quantity', 'yan_lot_id')
    def onchange_batch(self):
        if self.yan_lot_id and self.move_id.move_type=='out_invoice':
            if self.yan_lot_id.product_qty < self.quantity:
                batch_product_qty = self.yan_lot_id.product_qty
                self.yan_lot_id = False
                warning = {
                    'title': "Warning",
                    'message': _("Selected Lot do not have enough qty. %s qty needed and lot have only %s" %(self.quantity,batch_product_qty)),
                }
                return {'warning': warning}

            self.exp_date = self.yan_lot_id.use_date


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_default_warehouse(self):
        yan_warehouse_id = self.env.user.sudo().yan_warehouse_id
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        return yan_warehouse_id or warehouse_id

    @api.model
    def _get_default_picking_type(self):
        return self.env.user.sudo().yan_picking_type_id or False

    STATES = {'posted': [('readonly', True)]}

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', default=_get_default_warehouse, states=STATES)
    create_stock_moves = fields.Boolean("Create Stock Moves?", copy=False, states=STATES)
    picking_id = fields.Many2one('stock.picking', 'Picking', copy=False, states=STATES)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', copy=False, default=_get_default_picking_type, states=STATES)
    yan_location_id = fields.Many2one('stock.location', 'Src Location', copy=False, states=STATES)
    yan_location_dest_id = fields.Many2one('stock.location', 'Destiantion Location', copy=False, states=STATES)

    @api.onchange('warehouse_id','picking_type_id','move_type','create_stock_moves')
    def onchange_warehouse(self):
        if self.warehouse_id:
            if self.move_type == 'out_invoice':
                self.picking_type_id = self.warehouse_id.out_type_id.id
                self.yan_location_id = self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_src_id.id or self.warehouse_id.lot_stock_id.id
                self.yan_location_dest_id = self.picking_type_id.default_location_dest_id and self.picking_type_id.default_location_dest_id.id or self.partner_id.property_stock_customer.id

            elif self.move_type == 'in_invoice':
                self.picking_type_id = self.warehouse_id.in_type_id.id
                self.yan_location_id = self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_src_id.id or self.partner_id.property_stock_supplier.id
                self.yan_location_dest_id = self.picking_type_id.default_location_dest_id and self.picking_type_id.default_location_dest_id.id or self.warehouse_id.lot_stock_id.id

            elif self.move_type == 'out_refund':
                self.picking_type_id = self.warehouse_id.in_type_id.id
                self.yan_location_id =  self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_src_id.id or self.partner_id.property_stock_customer.id
                self.yan_location_dest_id = self.picking_type_id.default_location_dest_id and self.picking_type_id.default_location_dest_id.id or self.warehouse_id.lot_stock_id.id

            elif self.move_type == 'in_refund':
                self.picking_type_id = self.warehouse_id.out_type_id.id
                self.yan_location_id =  self.picking_type_id.default_location_src_id and self.picking_type_id.default_location_src_id.id or self.warehouse_id.lot_stock_id.id
                self.yan_location_dest_id = self.picking_type_id.default_location_dest_id and self.picking_type_id.default_location_dest_id.id or self.partner_id.property_stock_supplier.id

    def yan_check_picking_possibility(self):
        create_picking = False
        if any(inv_line.product_id and inv_line.product_id.type in ['consu','product'] for inv_line in self.invoice_line_ids):
            create_picking = True
        return create_picking

    @api.model
    def move_line_from_invoice_lines(self, picking, location_id, location_dest_id):
        StockMoveL = self.env['stock.move.line']
        for line in self.invoice_line_ids:
            if line.product_id and line.product_id.type!='service':
                StockMoveL.with_context(default_immediate_transfer=True).create({
                    'product_id': line.product_id.id,
                    #'product_uom_qty': line.quantity,
                    'product_uom_id': line.product_uom_id.id,
                    'date': fields.datetime.now(),                    
                    'picking_id': picking.id,
                    'picking_type_id': picking.picking_type_id.id,
                    'state': 'assigned',
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'lot_id': line.yan_lot_id and line.yan_lot_id.id or False, 
                    'lot_name': line.yan_lot_id and line.yan_lot_id.name or '', 
                    'yan_account_move_line_id': line.id, 
                    'qty_done': line.quantity,
                    'company_id': picking.company_id.id,
                    'package_level_id': False,
                })

    @api.model
    def yan_create_picking(self, picking_type_id, location_id, location_dest_id):
        MoveLine = self.env['stock.move.line']
        picking_id = self.env['stock.picking'].with_context(default_immediate_transfer=True).create({
            'partner_id': self.partner_id.id,
            'date': fields.datetime.now(), 
            'company_id': self.company_id.id,
            'picking_type_id': picking_type_id.id,
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'move_type': 'direct',
            'origin': self.name,
        })
        self.picking_id = picking_id.id
        self.move_line_from_invoice_lines(picking_id, location_id, location_dest_id)
        picking_id.button_validate()

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for inv in self:
            if inv.create_stock_moves and inv.yan_check_picking_possibility():
                if (not inv.picking_type_id) or (not inv.yan_location_id) or (not inv.yan_location_dest_id):
                    inv.onchange_warehouse()
                if inv.picking_type_id and inv.yan_location_id and inv.yan_location_dest_id:
                    inv.yan_create_picking(inv.picking_type_id, inv.yan_location_id, inv.yan_location_dest_id)
        return res

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        if self.picking_id:
            self.picking_id.action_cancel()


class StockLot(models.Model):
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

