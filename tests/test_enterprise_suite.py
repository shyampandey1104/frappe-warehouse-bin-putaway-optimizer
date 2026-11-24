# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

import unittest
from putaway.controllers.base_controller import EnterpriseBaseController
from putaway.controllers.workflow_handler import WorkflowStateMachine
from putaway.services.integration_service import EnterpriseIntegrationService
from putaway.services.validator import EnterpriseValidationEngine
from putaway.tasks import hourly_sync, daily_reconciliation, weekly_digest
from putaway import api
from putaway.putaway_core.doctype.putaway_entry.putaway_entry import WarehouseBinPutawayOptimizerEntry
from putaway.putaway_core.doctype.putaway_item.putaway_item import WarehouseBinPutawayOptimizerItem
from putaway.putaway_core.doctype.putaway_settings.putaway_settings import WarehouseBinPutawayOptimizerSettings
from putaway.putaway_core.doctype.putaway_audit_log.putaway_audit_log import WarehouseBinPutawayOptimizerAuditLog
from putaway.putaway_core.report.putaway_summary.putaway_summary import execute as run_report

class TestEnterpriseArchitecture(unittest.TestCase):
    def setUp(self):
        self.entry = WarehouseBinPutawayOptimizerEntry()
        self.entry.title = "Test Frappe Warehouse Bin Putaway Optimizer"
        self.entry.party = "Alpha Enterprise Corp"
        self.entry.status = "Draft"

        item1 = WarehouseBinPutawayOptimizerItem()
        item1.item_code = "ITEM-001"
        item1.qty = 10.0
        item1.rate = 1500.0
        item1.validate()

        item2 = WarehouseBinPutawayOptimizerItem()
        item2.item_code = "ITEM-002"
        item2.qty = 5.0
        item2.rate = 2000.0
        item2.validate()

        self.entry.items = [item1, item2]

    def test_multi_doctype_aggregation(self):
        self.entry.validate()
        self.assertEqual(self.entry.total_qty, 15.0)
        self.assertEqual(self.entry.total_amount, 25000.0)
        self.assertEqual(self.entry.grand_total, 25000.0)

    def test_submission_and_cancellation_lifecycle(self):
        self.entry.validate()
        self.entry.on_submit()
        self.assertEqual(self.entry.status, "Submitted")
        self.assertEqual(self.entry.audit_status, "Compliant")

        self.entry.on_cancel()
        self.assertEqual(self.entry.status, "Cancelled")
        self.assertEqual(self.entry.audit_status, "Flagged")

    def test_workflow_state_machine(self):
        self.assertTrue(WorkflowStateMachine.apply_transition(self.entry, "Pending Review"))
        self.assertEqual(self.entry.status, "Pending Review")
        self.assertTrue(WorkflowStateMachine.apply_transition(self.entry, "Approved"))
        self.assertEqual(self.entry.status, "Approved")

    def test_settings_single_doctype(self):
        settings = WarehouseBinPutawayOptimizerSettings()
        settings.batch_size = 500
        settings.validate()
        res = settings.test_connection()
        self.assertEqual(res["status"], "success")

    def test_tamper_proof_audit_log(self):
        audit = WarehouseBinPutawayOptimizerAuditLog()
        audit.reference_doctype = "Frappe Warehouse Bin Putaway Optimizer Entry"
        audit.reference_name = "TEST-REF-001"
        audit.action = "Submitted"
        audit.before_insert()
        self.assertIsNotNone(audit.checksum_hash)
        self.assertEqual(len(audit.checksum_hash), 64)

    def test_script_report_execution(self):
        columns, data, message, chart, summary = run_report()
        self.assertTrue(len(columns) >= 5)
        self.assertTrue(len(data) >= 1)
        self.assertIsNotNone(chart)
        self.assertTrue(len(summary) >= 2)

    def test_api_endpoints(self):
        ping_res = api.ping()
        self.assertEqual(ping_res["status"], "ok")

        overview = api.get_status_overview()
        self.assertEqual(overview["operational_status"], "ONLINE")
        self.assertEqual(len(overview["doctypes"]), 4)

    def test_scheduler_background_tasks(self):
        self.assertEqual(hourly_sync()["status"], "COMPLETED")
        self.assertEqual(daily_reconciliation()["status"], "VERIFIED_100_PERCENT")
        self.assertEqual(weekly_digest()["status"], "DISPATCHED")

if __name__ == "__main__":
    unittest.main()
