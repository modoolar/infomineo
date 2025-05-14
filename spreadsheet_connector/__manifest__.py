# -*- coding: utf-8 -*-
{
    'name': "Odoo to Sheets Connector",

    'summary': """
       	Odoo to Google Spreadsheet Connector, spread sheet, google sheets, excel sheets, microsoft excel, powerbi, power bi, ms excel, ms office, microsoft office,
    Data connection and synchronization,
    Excel Connector for Odoo Data,
    PowerBI Connector for Odoo Data,
    Power BI Connector for Odoo Data,
    Odoo Excel Connector LibreOffice,
    Odoo Excel Data Connector,
    LibreOffice Connector excel to database,
    Excel Connect to Odoo,
    Excel Office Document Connection to Odoo,
    LibreOffice Connect excel to Odoo Data,
    Generate ODC Odoo, 
    Excel Data Connection Template, 
    Auto synchronization data,
    LibreOffice Sync data to excel,
    ERP Excel Data Connection LibreOffice,
    Office Document Connection for Odoo,
    Export Odoo Data Excel,
    Excel Report Connector,
    Project Tasks to Excel,
    Accounting Report to Excel,
    Connect Account Report to Excel,
    LibreOffice Calc Link External Data from Odoo,
    OpenOffice Link External Data from Odoo,
    All In One Excel Report,
    All In One Report,
    Quotations Excel Report,
    Sale Order Excel Report,
    Sales Order Excel Report,
    Request For Quotation Excel Report,
    RFQ Excel Report,
    Supplier Invoice Excel Report,
    Customer Invoice Excel Report,
    Invoice Excel Report,
    Invoice Report,
    Invoices Excel Report,
    Delivery Order Excel Report,
    Delivery Order Report,
    XLS Report,
    XLSX Report,
    
       """,

    'description': """
        	Spread Sheets Connector Module for Odoo
    """,

    'author': "TechFinna",
    'website': "https://techfinna.com/googlesheet-odoo-connector",
    'category': 'Connector',
    'price': 249,
    'currency': 'USD',
    'version': '2.0.2',
    'installable': True,
    'live_test_url': 'https://techfinna.com/demo/odoo-google-spreadsheet-connector/',
    'support': "info@techfinna.com",
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'depends': ['base', 'web'],
    'images': ['static/description/banner.gif'],
    "external_dependencies": {"python": ["pip"]},

    # always loaded
    'data': [
        'views/settings.xml',

    ],
    'assets': {
        'spreadsheet_connector.ass': [
            'spreadsheet_connector/views/sty.css'
        ]
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application": True,
    "installable": True,
    
}
