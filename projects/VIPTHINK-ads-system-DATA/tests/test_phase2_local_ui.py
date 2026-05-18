import shutil
import tempfile
import unittest
from pathlib import Path

from meta_ads_closed_loop.app.local_ui.build import build_local_ui, build_ui_data


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "meta_audit_dataset_minimal.json"


class Phase2LocalUITests(unittest.TestCase):
    def test_build_ui_data_exposes_first_closed_loop(self):
        data = build_ui_data(FIXTURE_PATH)

        self.assertEqual(data["snapshot"]["account_name"], "示例 Meta 投放账户")
        self.assertEqual(data["workflow"][0], "账户总览")
        self.assertEqual(data["workflow"][-1], "报表复盘")
        self.assertEqual(len(data["accounts"]), 1)
        self.assertGreaterEqual(len(data["diagnoses"]), 2)
        self.assertGreaterEqual(len(data["drafts"]), 2)
        self.assertEqual(len(data["blockedActions"]), 1)
        self.assertIn("ctr", data["snapshot"]["campaigns"][0])
        self.assertIn("cpl", data["snapshot"]["campaigns"][0])
        self.assertIn("cpa", data["snapshot"]["campaigns"][0])
        self.assertEqual(len(data["snapshot"]["adsets"]), 1)
        self.assertEqual(len(data["snapshot"]["ads"]), 1)
        self.assertEqual(len(data["drilldown"]["campaigns"]), 2)
        self.assertEqual(data["drilldown"]["campaigns"][0]["adset_count"], 1)
        self.assertEqual(data["drilldown"]["campaigns"][0]["ad_count"], 1)
        self.assertEqual(data["drilldown"]["campaigns"][0]["adsets"][0]["ads"][0]["name"], "AI REDACTED_PRODUCTcreative_asset A")
        self.assertIn("landing_page_views", data["drilldown"]["campaigns"][0])
        self.assertIn("ctr", data["drilldown"]["campaigns"][0]["adsets"][0])
        self.assertIn("cpl", data["drilldown"]["campaigns"][0]["adsets"][0]["ads"][0])

    def test_build_local_ui_writes_static_app_without_real_secret_shapes(self):
        tmpdir = Path(tempfile.mkdtemp())
        try:
            html_path = build_local_ui(output_dir=tmpdir, fixture_path=FIXTURE_PATH)
            data_js = (tmpdir / "data.js").read_text(encoding="utf-8")
            html = html_path.read_text(encoding="utf-8")

            self.assertTrue(html_path.exists())
            self.assertTrue((tmpdir / "app.js").exists())
            self.assertTrue((tmpdir / "styles.css").exists())
            self.assertIn("账户总览", html)
            self.assertIn("Campaign 下钻", html)
            self.assertIn("adsetDrilldownTable", html)
            self.assertIn("adDrilldownTable", html)
            self.assertIn("安全确认", html)
            self.assertIn("window.META_CLOSED_LOOP_DATA", data_js)
            self.assertIn("示例 Meta 投放账户", data_js)
            self.assertNotIn("access_token", data_js)
            self.assertNotIn("EAA", data_js)
            self.assertNotIn("act_", data_js)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
