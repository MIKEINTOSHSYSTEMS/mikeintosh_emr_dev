# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020-Today Entrivis Tech PVT. LTD. (<http://www.entrivistech.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'Website Page HTML Code',
    'category': 'Website/Website',
    'summary': 'Insert custom html code specific to a website page.',
    "version": "16.0.1.0.0",
    'description': """This Module is used to set website page specific custom code.""",
    'author': 'Entrivis Tech Pvt. Ltd.',
    'website': 	'https://www.entrivistech.com',
    'depends': ['website'],
    'data': [
        'views/templates.xml',
        'views/website_pages.xml',
    ],
    'images': ['static/description/Entrivis_Website_Page_Custom_Code.gif'],
    'installable': True,
    'license': 'LGPL-3',

}
