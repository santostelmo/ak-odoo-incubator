# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def manage_subcontracted_manufacture_line(self, line):
        self.ensure_one()
        supplier = self.partner_id
        if line._is_service_procurement():
            mo = line.mo_id
            supplier_wh, supplier_loc = supplier.\
                _get_supplier_wh_and_location()
            if mo.location_dest_id != supplier_loc:
                mo.update_locations(supplier_wh, supplier_loc)
                mo.cancel_row_move_ids()
                mo.rebuild_raw_move_ids()
                moves_out, moves_out_dest = (
                    mo.update_moves_after_production(
                        supplier, supplier_wh, supplier_loc)
                )
            else:
                # in order to link existing move to po
                moves_out, moves_out_dest = (
                    mo.get_expedition_and_reception_moves()
                )

            # po.picking_type_id (Supplier/manufacture)
            self.picking_type_id = supplier_wh.manu_type_id.id

            # Link picking out of the vendor (supplier)
            # and picking in of the destination (us or the next supplier)
            self.add_purchase_line_id(moves_out, line)
            self.add_purchase_line_id(moves_out_dest, line)
            return

    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        for purchase in self:
            for line in purchase.order_line:
                # In seperate method as it is reused in an other module
                purchase.manage_subcontracted_manufacture_line(line)
        return res

    def add_purchase_line_id(self, moves, line):
        '''Add the reference to this PO.
        Only moves in the picking
        '''
        self.ensure_one()
        moves.write({'purchase_line_id': line.id})