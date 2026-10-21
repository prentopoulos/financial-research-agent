import os
import unittest

os.environ["LANGSMITH_TRACING"] = "false"

from backend.app.analysis import calculate_valuation, extract_financials, safe_div
from backend.app.inline_xbrl import InlineDocument
from backend.app.models import Financials
from backend.app.security import AccessTriangle, SecurityBoundaryError
from backend.app.workflow import fallback_peer_tickers


class AnalysisTests(unittest.TestCase):
    @staticmethod
    def facts(tag: str, rows: list[dict], namespace: str = "us-gaap") -> dict:
        return {"facts": {namespace: {tag: {"units": {"USD": rows}}}}}

    def test_safe_div_handles_missing_or_zero_denominator(self):
        self.assertIsNone(safe_div(10, 0))
        self.assertIsNone(safe_div(10, None))
        self.assertEqual(safe_div(10, 2), 5)

    def test_valuation_uses_reported_values(self):
        financials = Financials(
            fiscal_year=2025,
            period_end="2025-12-31",
            revenue=100,
            revenue_growth=0.25,
            gross_margin=0.7,
            operating_margin=0.5,
            net_margin=0.4,
            free_cash_flow=30,
            cash=20,
            debt=5,
        )
        valuation = calculate_valuation(financials, shares=10, price=20, as_of="2026-01-02")
        self.assertEqual(valuation.market_cap, 200)
        self.assertEqual(valuation.pe, 5)
        self.assertEqual(valuation.price_to_sales, 2)
        self.assertEqual(valuation.fcf_yield, 0.15)

    def test_access_triangle_rejects_all_three_capabilities(self):
        boundary = AccessTriangle(untrusted_input=True, sensitive_data=True, external_egress=True)
        with self.assertRaises(SecurityBoundaryError):
            boundary.enforce()

    def test_access_triangle_allows_two_capabilities(self):
        AccessTriangle(untrusted_input=True, sensitive_data=False, external_egress=True).enforce()

    def test_peer_fallback_is_industry_specific_and_excludes_subject(self):
        self.assertEqual(fallback_peer_tickers("3674", "NVDA"), ["AMD", "INTC"])
        self.assertEqual(fallback_peer_tickers("3571", "XNDU", "Xanadu Quantum Technologies"), ["IONQ", "RGTI"])
        self.assertEqual(fallback_peer_tickers("7373", "QNT", "Quantinuum Inc."), ["IONQ", "RGTI"])

    def test_20f_annual_financials_are_supported(self):
        facts = self.facts("Revenue", [
            {"form": "20-F", "fy": 2024, "start": "2024-01-01", "end": "2024-12-31", "filed": "2025-03-01", "val": 80},
            {"form": "20-F", "fy": 2025, "start": "2025-01-01", "end": "2025-12-31", "filed": "2026-03-01", "val": 100},
        ], namespace="ifrs-full")
        financials, _ = extract_financials(facts)
        self.assertEqual(financials.basis, "annual")
        self.assertEqual(financials.source_form, "20-F")
        self.assertEqual(financials.revenue_growth, 0.25)

    def test_prospectus_annual_financials_are_limited_history(self):
        facts = self.facts("Revenues", [
            {"form": "F-1", "start": "2024-01-01", "end": "2024-12-31", "filed": "2026-05-01", "val": 40},
            {"form": "F-1", "start": "2025-01-01", "end": "2025-12-31", "filed": "2026-05-01", "val": 50},
        ])
        financials, _ = extract_financials(facts)
        self.assertEqual(financials.basis, "prospectus")
        self.assertTrue(financials.limited_history)

    def test_ttm_uses_annual_plus_current_ytd_less_prior_ytd(self):
        facts = self.facts("Revenues", [
            {"form": "10-K", "fy": 2025, "start": "2025-01-01", "end": "2025-12-31", "filed": "2026-02-01", "val": 100},
            {"form": "10-Q", "fy": 2026, "start": "2025-01-01", "end": "2025-06-30", "filed": "2026-08-01", "val": 40},
            {"form": "10-Q", "fy": 2026, "start": "2026-01-01", "end": "2026-06-30", "filed": "2026-08-01", "val": 60},
        ])
        financials, _ = extract_financials(facts)
        self.assertEqual(financials.basis, "ttm")
        self.assertEqual(financials.revenue, 120)
        self.assertAlmostEqual(financials.revenue_growth or 0, 0.2)

    def test_recent_ipo_interim_is_annualized_and_low_history(self):
        facts = self.facts("Revenues", [
            {"form": "10-Q", "fy": 2026, "start": "2025-01-01", "end": "2025-06-30", "filed": "2026-08-01", "val": 50},
            {"form": "10-Q", "fy": 2026, "start": "2026-01-01", "end": "2026-06-30", "filed": "2026-08-01", "val": 60},
        ])
        financials, _ = extract_financials(facts)
        self.assertEqual(financials.basis, "interim_annualized")
        self.assertTrue(financials.limited_history)
        self.assertAlmostEqual(financials.revenue_growth or 0, 0.2)

    def test_inline_xbrl_extension_revenue_tag_is_supported(self):
        html = """
        <xbrli:context id="annual"><xbrli:entity><xbrli:identifier>1</xbrli:identifier></xbrli:entity>
        <xbrli:period><xbrli:startDate>2025-01-01</xbrli:startDate><xbrli:endDate>2025-12-31</xbrli:endDate></xbrli:period></xbrli:context>
        <xbrli:context id="class-a"><xbrli:entity><xbrli:identifier>1</xbrli:identifier><xbrli:segment>
        <xbrldi:explicitMember dimension="dei:StatementClassOfStockAxis">issuer:ClassAMember</xbrldi:explicitMember>
        </xbrli:segment></xbrli:entity><xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period></xbrli:context>
        <xbrli:context id="class-b"><xbrli:entity><xbrli:identifier>1</xbrli:identifier><xbrli:segment>
        <xbrldi:explicitMember dimension="dei:StatementClassOfStockAxis">issuer:ClassBMember</xbrldi:explicitMember>
        </xbrli:segment></xbrli:entity><xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period></xbrli:context>
        <ix:nonFraction name="issuer:TotalRevenue" contextRef="annual" unitRef="USD" scale="3">125</ix:nonFraction>
        <ix:nonFraction name="dei:EntityCommonStockSharesOutstanding" contextRef="class-a" unitRef="shares">10</ix:nonFraction>
        <ix:nonFraction name="dei:EntityCommonStockSharesOutstanding" contextRef="class-b" unitRef="shares">20</ix:nonFraction>
        """
        document = InlineDocument(form="F-1", filed="2026-05-01", url="https://www.sec.gov/example", html=html)
        financials, shares = extract_financials({"facts": {}}, [document])
        self.assertEqual(financials.revenue, 125000)
        self.assertEqual(financials.basis, "prospectus")
        self.assertEqual(shares, 30)


if __name__ == "__main__":
    unittest.main()
