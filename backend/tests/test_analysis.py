import unittest

from backend.app.analysis import calculate_valuation, safe_div
from backend.app.models import Financials
from backend.app.security import AccessTriangle, SecurityBoundaryError
from backend.app.workflow import fallback_peer_tickers


class AnalysisTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
