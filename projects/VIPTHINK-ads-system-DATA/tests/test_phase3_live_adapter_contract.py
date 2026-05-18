import unittest
from urllib.parse import parse_qs, urlparse

from meta_ads_closed_loop.adapters.meta_readonly.live import (
    LiveMetaReadonlyAdapter,
    MetaGraphReadonlyClient,
    MetaReadonlyConfig,
    load_env_text,
    redact_token,
)


class Phase3LiveAdapterContractTests(unittest.TestCase):
    def test_load_env_text_and_redaction_do_not_expose_full_token(self):
        env = load_env_text("META_ACCESS_TOKEN='DUMMY_TEST_TOKEN_VALUE'\nMETA_AD_ACCOUNT_ID=123\n")

        self.assertEqual(env["META_ACCESS_TOKEN"], "DUMMY_TEST_TOKEN_VALUE")
        self.assertEqual(redact_token(env["META_ACCESS_TOKEN"]), "DUMM...ALUE")

    def test_live_client_uses_get_urls_with_access_token_query(self):
        seen_urls = []

        def fake_transport(url, timeout):
            seen_urls.append(url)
            return {"data": []}

        client = MetaGraphReadonlyClient(
            MetaReadonlyConfig(access_token="DUMMY_TEST_TOKEN_VALUE", api_version="v25.0"),
            transport=fake_transport,
        )
        client.list_ad_accounts(max_pages=1)

        parsed = urlparse(seen_urls[0])
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.path, "/v25.0/me/adaccounts")
        self.assertEqual(query["access_token"], ["DUMMY_TEST_TOKEN_VALUE"])
        self.assertIn("fields", query)

    def test_live_adapter_normalizes_account_tree_without_write_methods(self):
        def fake_transport(url, timeout):
            parsed = urlparse(url)
            path = parsed.path
            query = parse_qs(parsed.query)
            if path.endswith("/me/adaccounts"):
                return {
                    "data": [
                        {
                            "id": "act_111",
                            "name": "示例账户",
                            "currency": "USD",
                            "timezone_name": "Asia/Shanghai",
                            "account_status": 1,
                        }
                    ]
                }
            if path.endswith("/act_111"):
                return {
                    "id": "act_111",
                    "name": "示例账户",
                    "currency": "USD",
                    "timezone_name": "Asia/Shanghai",
                    "account_status": 1,
                }
            if path.endswith("/campaigns"):
                return {"data": [{"id": "c_live", "name": "示例 Campaign", "effective_status": "ACTIVE"}]}
            if path.endswith("/adsets"):
                return {"data": [{"id": "s_live", "name": "示例 Ad Set", "campaign_id": "c_live", "effective_status": "ACTIVE"}]}
            if path.endswith("/ads"):
                return {
                    "data": [
                        {
                            "id": "a_live",
                            "name": "示例广告",
                            "campaign_id": "c_live",
                            "adset_id": "s_live",
                            "creative": {"id": "creative_1", "name": "creative_asset A", "thumbnail_url": "https://example.test/?access_token=SHOULD_NOT_LEAK"},
                            "effective_status": "ACTIVE",
                        }
                    ]
                }
            if path.endswith("/insights"):
                level = query["level"][0]
                if level == "campaign":
                    return {
                        "data": [
                            {
                                "campaign_id": "c_live",
                                "campaign_name": "示例 Campaign",
                                "spend": "50",
                                "impressions": "1000",
                                "inline_link_clicks": "20",
                                "actions": [{"action_type": "lead", "value": "2"}],
                            }
                        ]
                    }
                if level == "adset":
                    return {
                        "data": [
                            {
                                "campaign_id": "c_live",
                                "campaign_name": "示例 Campaign",
                                "adset_id": "s_live",
                                "adset_name": "示例 Ad Set",
                                "spend": "50",
                                "actions": [{"action_type": "lead", "value": "2"}],
                            }
                        ]
                    }
                return {
                    "data": [
                        {
                            "campaign_id": "c_live",
                            "campaign_name": "示例 Campaign",
                            "adset_id": "s_live",
                            "adset_name": "示例 Ad Set",
                            "ad_id": "a_live",
                            "ad_name": "示例广告",
                            "spend": "50",
                            "inline_link_clicks": "20",
                            "actions": [{"action_type": "landing_page_view", "value": "12"}],
                        }
                    ]
                }
            raise AssertionError(f"unexpected url {url}")

        config = MetaReadonlyConfig(access_token="DUMMY_TEST_TOKEN_VALUE", api_version="v25.0", default_account_id="act_111")
        client = MetaGraphReadonlyClient(config, transport=fake_transport)
        adapter = LiveMetaReadonlyAdapter(config, client=client)

        accounts = adapter.fetch_accounts()
        snapshot = adapter.fetch_snapshot()

        self.assertEqual(len(accounts), 1)
        self.assertEqual(snapshot.account_name, "示例账户")
        self.assertEqual(snapshot.campaigns[0].name, "示例 Campaign")
        self.assertEqual(snapshot.adsets[0].name, "示例 Ad Set")
        self.assertEqual(snapshot.ads[0].creative["name"], "creative_asset A")
        self.assertNotIn("SHOULD_NOT_LEAK", str(snapshot.ads[0].creative))
        self.assertFalse(hasattr(adapter, "pause"))
        self.assertFalse(hasattr(adapter, "update_budget"))


if __name__ == "__main__":
    unittest.main()
