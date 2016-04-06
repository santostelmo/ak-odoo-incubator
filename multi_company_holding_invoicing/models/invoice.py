# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    holding_sale_ids = fields.One2many('sale.order', 'holding_invoice_id')
    holding_sale_count = fields.Integer(
        compute='_holding_sale_count', string='# of Sales Order')
    sale_count = fields.Integer(
        compute='_sale_count', string='# of Sales Order')
    child_invoice_ids = fields.One2many(
        'account.invoice', 'holding_invoice_id')
    child_invoice_count = fields.Integer(
        compute='_child_invoice_count', string='# of Invoice')
    holding_invoice_id = fields.Many2one('account.invoice', 'Holding Invoice')

    @api.multi
    def _holding_sale_count(self):
        for inv in self:
            inv.holding_sale_count = len(inv.holding_sale_ids)

    @api.multi
    def _sale_count(self):
        for inv in self:
            inv.sale_count = len(inv.sale_ids)

    @api.multi
    def _child_invoice_count(self):
        for inv in self:
            inv.child_invoice_count = len(inv.child_invoice_ids)

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            invoice.holding_sale_ids._set_invoice_state('invoiced')
        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def unlink(self):
        sale_obj = self.env['sale.order']
        sales = sale_obj.search([('holding_invoice_id', 'in', self.ids)])
        res = super(AccountInvoice, self).unlink()
        sales._set_invoice_state('invoiceable')
        return res

    @api.multi
    def generate_child_invoice(self):
        for invoice in self:
            child_invoices = self.holding_sale_ids.action_child_invoice()
            child_invoices.write({'holding_invoice_id': invoice.id})
            for child_invoice in child_invoices:
                child_invoice.signal_workflow('invoice_open')
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_line_ids = fields.Many2many(
        comodel_name='account.invoice.line',
        relation='sale_order_line_invoice_rel',
        column1='invoice_id',
        column2='order_line_id')