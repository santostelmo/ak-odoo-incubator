# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{'name': 'Purchase Supplier Delay',
 'version': '0.1',
 'author': 'Akretion,Odoo Community Association (OCA)',
 'website': 'http://www.akretion.com',
 'description': """
 """,
 'license': 'AGPL-3',
 'category': 'Purchase Management',
 'summary': 'Re-calculate purchase line date planned on purchase validation',
 'depends': [
             'purchase',
             ],
 'data': [
      'company_view.xml',
      'partner_view.xml',
 ],
 'installable': True,
 }
