import json
import unittest
from pathlib import Path

import recover

FIXTURES = Path(__file__).parent / "fixtures"


class TestNormalizeUrl(unittest.TestCase):
    def test_strips_scheme_host_port(self):
        self.assertEqual(
            recover.normalize_url("http://drunk-robot.com:80/cosplay-faux-pas/"),
            "/cosplay-faux-pas/",
        )

    def test_strips_www_and_adds_trailing_slash(self):
        self.assertEqual(
            recover.normalize_url("http://www.drunk-robot.com/2011/05/23/cosplay-faux-pas"),
            "/2011/05/23/cosplay-faux-pas/",
        )

    def test_keeps_p_query(self):
        self.assertEqual(
            recover.normalize_url("http://drunk-robot.com:80/?p=155"),
            "/?p=155",
        )

    def test_drops_other_queries(self):
        self.assertEqual(
            recover.normalize_url(
                "http://drunk-robot.com/wp-includes/js/jquery/jquery.js?ver=1.8.3"
            ),
            "/wp-includes/js/jquery/jquery.js",
        )


class TestClassify(unittest.TestCase):
    def test_root_slug_is_post(self):
        self.assertEqual(recover.classify("/cosplay-faux-pas/"), "post-slug")

    def test_numeric_slug_is_post(self):
        self.assertEqual(recover.classify("/05142006/"), "post-slug")

    def test_dated_url_is_post(self):
        self.assertEqual(recover.classify("/2011/05/23/cosplay-faux-pas/"), "post-dated")

    def test_p_id(self):
        self.assertEqual(recover.classify("/?p=155"), "p-id")

    def test_listing_pages(self):
        self.assertEqual(recover.classify("/category/comics/"), "listing")
        self.assertEqual(recover.classify("/category/comics/page/2/"), "listing")
        self.assertEqual(recover.classify("/author/admin/"), "listing")

    def test_feeds(self):
        self.assertEqual(recover.classify("/feed/"), "feed")
        self.assertEqual(recover.classify("/cosplay-faux-pas/feed/"), "feed")

    def test_assets_and_wp_internals(self):
        self.assertEqual(recover.classify("/comics/2011-05-23.gif"), "asset")
        self.assertEqual(recover.classify("/wp-content/themes/newdr/style.css"), "other")
        self.assertEqual(recover.classify("/favicon.ico"), "asset")

    def test_homepage_is_other(self):
        self.assertEqual(recover.classify("/"), "other")

    def test_degenerate_path_is_other(self):
        self.assertEqual(recover.classify("//"), "other")


class TestBestSnapshot(unittest.TestCase):
    def rows(self, *specs):
        # spec: (timestamp, statuscode)
        return [
            ["com,drunk-robot)/x", ts, "http://drunk-robot.com/x/", "text/html", sc, "DIGEST", "1000"]
            for ts, sc in specs
        ]

    def test_prefers_latest_200_before_2017(self):
        rows = self.rows(("20130903160646", "200"), ("20150210132659", "200"), ("20230203044456", "200"))
        self.assertEqual(recover.best_snapshot(rows), "20150210132659")

    def test_falls_back_to_any_200(self):
        rows = self.rows(("20210210181359", "200"),)
        self.assertEqual(recover.best_snapshot(rows), "20210210181359")

    def test_ignores_non_200(self):
        rows = self.rows(("20150210132659", "301"), ("20130903160646", "200"))
        self.assertEqual(recover.best_snapshot(rows), "20130903160646")

    def test_none_when_no_200(self):
        rows = self.rows(("20150210132659", "301"),)
        self.assertIsNone(recover.best_snapshot(rows))


class TestCdxFixture(unittest.TestCase):
    def test_fixture_discovers_known_posts(self):
        with open(FIXTURES / "cdx_sample.json") as f:
            rows = json.load(f)[1:]
            paths = {recover.normalize_url(r[2]) for r in rows}
            posts = {p for p in paths if recover.classify(p) in ("post-slug", "post-dated")}
            self.assertIn("/cosplay-faux-pas/", posts)
            self.assertIn("/2011/06/20/dance-of-madness/", posts)
            self.assertIn("/05142006/", posts)
            self.assertGreater(len(posts), 40)


if __name__ == "__main__":
    unittest.main()
