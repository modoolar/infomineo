# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo Sale",
    "summary": "Infomineo specific extensions around Sale app",
    "version": "15.0.0.8.0",
    "category": "Sale",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "sale_management",
        "sale_order_description",
        "sale_second_sales_person",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
    ],
}
