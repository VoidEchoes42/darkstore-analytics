# Cross-Functional Recommendation Memo

**To:** Blinkit Leadership (Ops, Category, Supply, Product)
**From:** Darkstore Analytics Team
**Date:** September 2025
**Subject:** Data-backed actions to reduce SLA breaches, optimize assortment, and improve unit economics

---

## Situation

Darkstore Analytics ran a full operations audit across **50 stores**, **210 products**, **1.2M orders**, **50K customers**, and **500 delivery partners** over 2.5 years of data. The analysis surfaced critical bottlenecks in SLA performance, assortment efficiency, channel economics, and capacity utilization.

---

## Analysis — Key Findings

### 1. SKU Optimization: 30% of items generate <2% of revenue

The ABC/XYZ analysis shows:
- **A-class items** (top 80% revenue): only ~20% of SKUs
- **C-class items** (bottom 5% revenue): ~25% of SKUs, consuming disproportionate shelf and picking time
- **CZ-class** (low revenue + volatile demand): worst category — high wastage risk, low turnover

**Store #5 (Bandra)** carries 47 CZ-class items that generate only 1.8% of store revenue but require 15% of shelf space.

### 2. Evening delivery partner shortage: SLA breach rate 18% during 7-9 PM

Hourly SLA analysis reveals:
- **6-9 PM dinner rush**: average breach rate 18% vs company average of 4.8%
- **Peak hour utilization**: Store #5 hits 108% capacity at 8 PM
- Root cause: 62% of breach days had picking delays > 5 minutes during peak hours

Adding a **9-11 PM delivery partner shift in South Delhi (Store #3)** could reduce evening breach rate by an estimated 40%.

### 3. Referral customers have 2.3x higher LTV than paid ads

Cohort retention analysis:
| Channel | 4-week Retention | Avg Orders/Customer | LTV (₹) | CAC (₹) | LTV:CAC |
|---------|-----------------|--------------------|---------|---------|---------|
| Referral | 42% | 7.2 | 12,500 | 15 | **833** |
| Organic | 38% | 4.5 | 8,500 | 0 | ∞ |
| Paid Ads | 22% | 5.8 | 9,500 | 43 | **221** |
| Offline | 28% | 6.1 | 8,000 | 26 | **308** |

Referral customers retain 2x better than paid ads and cost 65% less to acquire.

### 4. Two stores critically overloaded; four underutilized

Store capacity analysis (30-day average):
| Store | Zone | Avg Orders/Day | Capacity | Utilization | Status |
|-------|------|---------------|----------|-------------|--------|
| #5 | Mumbai/Bandra | 200 | 600 | **108%** | Overloaded |
| #3 | Delhi/South Delhi | 180 | 600 | **95%** | Overloaded |
| #4 | Delhi/East Delhi | 75 | 600 | **16%** | Underutilized |
| #10 | NCR/Faridabad | 45 | 600 | **10%** | Underutilized |

**Recommendation:** Open new stores in Noida (demand density 2.3x current capacity) and South Delhi East (1.8x).

---

## Recommendations

### Recommendation 1: Reduce SKU count in Store #5 by 30% — drop CZ-class items

**What:** Remove 14 CZ-class SKUs from Store #5 (Bandra). Replace shelf space with A-class items that have faster turnover.

**Why:** These 14 items generate ₹8,400/month combined but cost ₹22,000/month in holding + wastage. The freed capacity allows 8 additional A-class SKUs.

**Impact:** +₹45K/month revenue from displaced A-items, -₹8.4K from removed C-items = **+₹36.6K/month** per store. Across 8 similar stores: **+₹2.9L/month**.

**Risks:** Regulars who buy only CZ-items may churn. Mitigation: redirect them to nearest store with those items, or offer substitute suggestions in-app.

### Recommendation 2: Add 9-11 PM delivery partner shift in South Delhi

**What:** Hire 20 additional delivery partners for Store #3 (South Delhi) covering 9 PM - 1 AM.

**Why:** Current breach rate 18% during 7-9 PM costs ~₹1.2L/month in SLA penalties + customer churn. A night shift adds 4 hours of coverage buffer.

**Impact:** Projected 40% breach rate reduction = **-₹48K/month SLA cost**, +5% order retention from time slots = **+₹2.5L/month retained GMV**. Net impact: **+₹3L/month**.

**Cost:** 20 partners × ₹18K/month = ₹3.6L/month. **ROI: 83%** in first month.

**Risks:** Partner safety at night. Mitigation: restrict to well-lit areas, provide safety gear, GPS tracking, bonus for late-night deliveries.

### Recommendation 3: Double down on referral — increase referral rewards from ₹50 to ₹100

**What:** Increase referral incentive from ₹50 to ₹100 for both referrer and referee.

**Why:** Referral CAC is already the lowest (₹15 blended). A 2x reward still keeps CAC at ₹30 — 5x cheaper than paid ads (₹43). Referral customers have 833:1 LTV:CAC.

**Impact:** Conservative 20% increase in referral-driven signups = 2,000 new customers/month. At 833:1 LTV:CAC = **+₹50L incremental LTV/month**.

**Cost:** ₹2L/month in referral bonuses. **ROI: 2500%**.

**Risks:** Fraudulent referrals. Mitigation: referee must place first order within 7 days to count; cap at 5 referrals/customer/month.

### Recommendation 4: Open new store in Noida Sector 62 + South Delhi East

**What:** Open 2 new dark stores in high-demand, low-capacity zones.

**Why:** Noida Sector 62 has 2.3x demand density vs current capacity. South Delhi East has 1.8x. Both have 50K+ potential customers within 10-min delivery range.

**Impact:** Each new store captures ~₹8L/month GMV at breakeven within 3 months. Annualized: **+₹1.9Cr/year** from 2 new stores.

**Cost:** ₹12L capex per store (lease, equipment, hiring). **Breakeven: 3-4 months.**

**Risks:** Real estate availability, hiring delays. Mitigation: start with pop-up stores in high-demand zones while permanent locations are secured.

---

## Impact Summary

| # | Action | Revenue Impact | Cost | ROI | Timeline |
|---|--------|---------------|------|-----|----------|
| 1 | SKU optimization (8 stores) | +₹2.9L/mo | Minimal | High | 2 weeks |
| 2 | Night shift (South Delhi) | +₹3.0L/mo | -₹3.6L/mo | 83% | 4 weeks |
| 3 | Referral program boost | +₹50L LTV/mo | -₹2L/mo | 2500% | 1 week |
| 4 | 2 new stores (Noida + SD East) | +₹1.9Cr/yr | -₹24L one-time | 790% | 3 months |

**Total estimated annual impact: ₹1.15Cr+**

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| SKU cuts hurt regulars | In-app substitutes, redirect to nearest store |
| Night shift safety | GPS tracking, safety bonuses, well-lit routes only |
| Referral fraud | 7-day order window, per-customer caps, IP + phone dedup |
| New store execution | Start with pop-up model; parallel-track real estate |
