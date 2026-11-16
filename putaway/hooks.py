# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "putaway"
app_title = "Frappe Warehouse Bin Putaway Optimizer"
app_publisher = "Shyamkumar Pandey"
app_description = "Frappe Warehouse Bin Putaway Optimizer for Frappe and ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/putaway/css/putaway.bundle.css"
app_include_js = "/assets/putaway/js/putaway.bundle.js"

# Document Events
# ---------------
doc_events = {
    "DocType Event": {
        "on_submit": "putaway.engine.on_document_submit",
        "on_cancel": "putaway.engine.on_document_cancel"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "putaway.engine.daily_scheduled_sync"
    ]
}
