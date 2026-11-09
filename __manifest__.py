{
    "name": "PopUpOps - Event Operations",
    "summary": "Event bookings, equipment estimates, and sales quotations",
    "version": "17.0.1.0.0",
    "category": "Services",
    "license": "LGPL-3",
    "author": "Independent learning project",
    "website": "",
    "depends": ["base", "mail", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "security/popup_ops_rules.xml",
        "data/sequence.xml",
        "views/booking_views.xml",
    ],
    "demo": ["demo/demo_data.xml"],
    "application": True,
    "installable": True,
}
