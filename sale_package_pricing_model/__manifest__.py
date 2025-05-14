# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Sale Package Pricing Model",
    "summary": "Sale Package Pricing Model",
    "version": "15.0.1.0.1",
    "category": "Sale",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": ["sale_order_template_type", "base_check_field_validity"],
    "data": [
        "security/ir.model.access.csv",
        "data/sale_order_template_data.xml",
        "demo/sale_package_configurator_demo.xml",
        "demo/sale_package_configurator_line_demo.xml",
        "demo/sale_order_template_demo.xml",
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
        "views/sale_order_template_views.xml",
        "views/sale_package_configurator_line_views.xml",
        "views/sale_package_configurator_views.xml",
    ],
}
