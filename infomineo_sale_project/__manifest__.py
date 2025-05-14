# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo Sale Project",
    "summary": "Functional extensions for sale project module",
    "version": "15.0.0.8.1",
    "category": "Sale/Project",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "infomineo_sale",
        "infomineo_project",
        "project_contact",
        "sale_project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/project_views.xml",
        "security/sale_security.xml",
    ],
}
