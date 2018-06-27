# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class PurchaseLineExtractorWizard(models.TransientModel):
    _name = 'purchase.line.extractor.wizard'

    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Deliver To')
    origin = fields.Char()
    date_order = fields.Date()
    order_reference = fields.Char()
    line_ids = fields.Many2many(
        comodel_name='purchase.order.extract.line',
        relation='extractor_wizard_purchase_line_extract_rel',
        column1='wizard_id',
        column2='line_id',
        string='Purchase Lines')

    @api.model
    def default_get(self, fields):
        res = super(PurchaseLineExtractorWizard, self).default_get(fields)
        extract_line_ids = self.env.context.get('active_ids', [])
        extract_lines = self.env['purchase.order.extract.line'].browse(
            extract_line_ids)
        pos = extract_lines.mapped('purchase_id')
        res['picking_type_id'] = pos[0].picking_type_id.id
        res['origin'] = ', '.join(pos.mapped('name'))
        res['date_order'] = pos[0].date_order
        res['line_ids'] = [(6, 0, extract_line_ids)]
        return res

    @api.multi
    def extract_po_line(self):
        self.ensure_one()
        copy_po_vals = {
            'picking_type_id': self.picking_type_id.id,
            'origin': self.origin,
            'order_line': False,
            'open_order': False,
            'date_order': self.date_order
        }
#        if self.order_reference:
#            copy_po_vals['name'] = self.order_reference
        new_po = self.line_ids[0].purchase_line_id.order_id.copy(copy_po_vals)
        for line in self.line_ids:
            purchase_line = line.purchase_line_id
            procs = purchase_line.procurement_ids
            move_dests = procs.mapped('move_dest_id')
            # Move this to write/create with open_order field?
            if move_dests:
                raise exceptions.Warning(
                    _('Extracting po line of purchase order coming from ' 
                      'make to order product is not possible.'))
            moves = purchase_line.move_ids.filtered(
                lambda m: m.state != 'cancel')
            if len(moves) != 1:
                raise exceptions.Warning(
                    _('Too much moves for product %s'
                      % purchase_line.product_id.default_code))
            if line.extract_quantity <= 0.0:
                raise exceptions.Warning(
                    _('The quantity to extract must be positive'))
            line.generate_new_po_line(new_po)
            line.update_quantity_extracted(moves)
        new_po.signal_workflow('purchase_confirm')
        new_po.signal_workflow('purchase_approve')

        action = self.env.ref(
            'purchase.purchase_form_action')
        result = action.read()[0]
        view = self.env.ref('purchase.purchase_order_form')
        result['views'] = [(view.id, 'form')]
        result['res_id'] = new_po.id
        return result
            
        
        
        
