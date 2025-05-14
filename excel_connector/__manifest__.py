# -*- coding: utf-8 -*-
{
    'name': "Odoo to Excel Connector - Seamless Data Integration",

    'summary': """
        Boost your Odoo analytics and reporting with the Odoo to Excel Connector. Easily export and integrate 
        your Odoo data into Excel for enhanced reporting, data visualization, and seamless connection with 
        Power BI and other BI tools.
        Odoo Excel connector, Odoo to Excel integration, Odoo data export to Excel, Odoo Excel reporting module, Odoo real-time data sync with Excel, Odoo Excel Power BI integration, Excel dashboard for Odoo, Odoo analytics in Excel, Odoo custom SQL export to Excel, Odoo financial reports in Excel, Odoo inventory management Excel export, Excel import for Odoo data, Odoo seamless Excel connection, Odoo data analytics with Excel, Odoo Excel connector module, Odoo Excel automation tool, Odoo Excel business intelligence, Odoo Excel add-on for reporting, Odoo ERP to Excel integration, Odoo custom reports in Excel.
        #OdooExcelConnector, #OdooToExcel, #OdooDataExport, #ExcelReportingModule, #PowerBIIntegration, #OdooExcelSync, #ExcelAnalytics, #BusinessIntelligence, #CustomSQLExport, #FinancialReports, #InventoryManagement, #RealTimeSync, #ExcelDataVisualization, #OdooERP, #OdooCustomReports, #ExcelAddOn, #OdooBIConnector, #OdooBusinessAnalytics, #DataIntegration, #DataConnectorModule, How to connect Odoo with Excel for reporting, Odoo real-time sync with Excel for data analytics, Export Odoo custom SQL data to Excel, Power BI integration with Odoo via Excel connector, Odoo ERP data import/export with Excel, Automate Odoo reporting in Excel spreadsheets, Best Odoo module for Excel integration, Financial reporting from Odoo to Excel, Inventory tracking in Excel with Odoo integration, Odoo data sync with Excel for advanced analytics.
        Microsoft Excel,Excel,Microsoft Excel integration with Odoo, Odoo to Microsoft Excel data sync, Microsoft Excel add-in for Odoo, Odoo real-time data in Microsoft Excel, Odoo ERP data in Excel spreadsheets, Microsoft Power BI and Odoo integration, Odoo custom reports in Microsoft Excel, Odoo automation with Microsoft Excel, Odoo financial data export to Microsoft Excel, Excel data import/export for Odoo, Odoo to Excel business intelligence, Microsoft Excel reporting for Odoo, Office 365 and Odoo integration, Excel Power Query for Odoo data, Odoo data analysis in Microsoft Excel, Microsoft Excel automation tool for Odoo, Odoo ERP connector for Excel and Power BI, Microsoft Power BI reports from Odoo, Microsoft Office 365 and Odoo synchronization, Odoo data analytics with Excel and Power BI
    """,

    'description': """
        The Odoo to Excel Connector module simplifies the process of connecting Odoo with Microsoft Excel. 
        Easily export Odoo data into Excel for better analytics, customizable reports, and dashboards. 
        This module is perfect for businesses looking to enhance their Odoo data insights, create dynamic 
        visualizations, and integrate with tools like Power BI for advanced analytics.

        Features:
        - Seamless Odoo to Excel data export and import
        - Real-time synchronization with Excel sheets
        - Compatible with Excel analytics tools like Power BI
        - Streamlined reporting for business analytics
        - Export data by table or custom SQL queries
        - Ideal for financial reports, inventory management, sales tracking, and more
    """,

    'author': "TechFinna",
    'website': "https://techfinna.com/",
    'category': 'Data Integration/Connector',
    'price': 149,
    'currency': 'USD',
    'version': '1.0',
    'installable': True,
    'live_test_url': 'https://techfinna.com/',
    'support': "info@techfinna.com",
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'depends': ['base', 'web'],

    'images': ['static/description/banner.png'],
    "external_dependencies": {"python": ["pip"]},  

    'data': [
        'views/settings.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
