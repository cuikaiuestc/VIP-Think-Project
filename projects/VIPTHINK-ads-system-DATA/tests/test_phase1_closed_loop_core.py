import unittest
from pathlib import Path

from meta_ads_closed_loop.adapters.meta_readonly import MockMetaReadonlyAdapter
from meta_ads_closed_loop.domain.diagnostics import diagnose_snapshot
from meta_ads_closed_loop.domain.drafts import create_local_draft
from meta_ads_closed_loop.domain.reports import build_closed_loop_report
from meta_ads_closed_loop.domain.safety import MetaWriteBlocker, WRITE_ACTIONS


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "meta_audit_dataset_minimal.json"


class Phase1ClosedLoopCoreTests(unittest.TestCase):
    def test_mock_readonly_adapter_normalizes_meta_snapshot(self):
        snapshot = MockMetaReadonlyAdapter(FIXTURE_PATH).fetch_snapshot()

        self.assertEqual(snapshot.account_name, "示例 Meta 投放账户")
        self.assertEqual(snapshot.currency, "USD")
        self.assertEqual(len(snapshot.campaigns), 2)
        self.assertEqual(len(snapshot.adsets), 1)
        self.assertEqual(len(snapshot.ads), 1)
        self.assertEqual(snapshot.total_spend, 340.5)
        self.assertEqual(snapshot.total_leads, 4)
        self.assertEqual(snapshot.total_purchases, 2)
        self.assertEqual(snapshot.total_landing_page_views, 80)
        self.assertEqual(snapshot.campaigns[0].landing_page_views, 80)
        self.assertEqual(snapshot.campaigns[0].ctr, 0.48)
        self.assertIsNone(snapshot.campaigns[0].cpl)
        self.assertEqual(snapshot.adsets[0].landing_page_views, 80)
        self.assertEqual(snapshot.ads[0].landing_page_views, 80)
        self.assertEqual(snapshot.ads[0].ctr, 0.0)

    def test_diagnostics_and_local_draft_do_not_require_write_api(self):
        snapshot = MockMetaReadonlyAdapter(FIXTURE_PATH).fetch_snapshot()
        diagnoses = diagnose_snapshot(snapshot)
        draft = create_local_draft(diagnoses[0], created_at="2026-05-17T10:05:00+08:00")

        self.assertGreaterEqual(len(diagnoses), 2)
        self.assertEqual(diagnoses[0].priority, "高")
        self.assertEqual(draft.status, "本地草稿")
        self.assertIn("不会调用 Meta 写接口", draft.body)

    def test_write_blocker_blocks_every_known_dangerous_action(self):
        blocker = MetaWriteBlocker()

        for action in WRITE_ACTIONS:
            with self.subTest(action=action):
                blocked = blocker.block(action, object_type="Campaign", object_id="campaign_high_spend_no_leads")
                self.assertEqual(blocked.action, action)
                self.assertIn("已被阻断", blocked.reason)

    def test_unknown_write_action_is_blocked_by_default(self):
        blocked = MetaWriteBlocker().block("mutate_anything", object_type="Ad", object_id="ad_001")

        self.assertEqual(blocked.action, "mutate_anything")
        self.assertIn("未知写动作", blocked.reason)

    def test_closed_loop_report_counts_readonly_diagnosis_drafts_and_blocks(self):
        snapshot = MockMetaReadonlyAdapter(FIXTURE_PATH).fetch_snapshot()
        diagnoses = diagnose_snapshot(snapshot)
        drafts = tuple(create_local_draft(item, created_at="2026-05-17T10:05:00+08:00") for item in diagnoses)
        blocked = (
            MetaWriteBlocker().block("pause", object_type="Campaign", object_id="campaign_high_spend_no_leads"),
        )

        report = build_closed_loop_report(snapshot, diagnoses, drafts, blocked)

        self.assertEqual(report.account_name, "示例 Meta 投放账户")
        self.assertEqual(report.diagnosis_count, len(diagnoses))
        self.assertEqual(report.draft_count, len(drafts))
        self.assertEqual(report.blocked_action_count, 1)
        self.assertIn("阻断 1 次危险写动作", report.summary)


if __name__ == "__main__":
    unittest.main()
