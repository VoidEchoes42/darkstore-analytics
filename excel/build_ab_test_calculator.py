"""
Generate ab_test_calculator.xlsx — Sample size, significance, power analysis.
"""
import os
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "excel"
OUTPUT_DIR.mkdir(exist_ok=True)


def auto_width(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max_len + 4, 30)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "excel"
OUTPUT_DIR.mkdir(exist_ok=True)


def sample_size_proportion(baseline: float, mde: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Calculate required sample size per group for a proportion test."""
    p1 = baseline
    p2 = baseline + mde
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    pooled = (p1 + p2) / 2
    n = ((z_alpha * (2 * pooled * (1 - pooled)) ** 0.5 + z_beta * (p1 * (1 - p1) + p2 * (1 - p2)) ** 0.5) / (p2 - p1)) ** 2
    return int(n) + 1


def z_test_proportion(n1: int, conv1: int, n2: int, conv2: int) -> dict:
    """Two-proportion z-test."""
    p1 = conv1 / n1
    p2 = conv2 / n2
    pooled_p = (conv1 + conv2) / (n1 + n2)
    se = (pooled_p * (1 - pooled_p) * (1/n1 + 1/n2)) ** 0.5
    if se == 0:
        return {"z": 0, "p_value": 1.0, "significant": False}
    z = (p1 - p2) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    return {
        "z": round(z, 4),
        "p_value": round(p_value, 4),
        "significant": p_value < 0.05,
        "p1_pct": round(p1 * 100, 2),
        "p2_pct": round(p2 * 100, 2),
    }


def build_ab_calculator():
    wb = Workbook()

    # ============================================================
    # Sheet 1: Sample Size Calculator
    # ============================================================
    ws = wb.active
    ws.title = "Sample Size Calculator"

    ws.append(["Sample Size Calculator"])
    ws.merge_cells("A1:D1")
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.append([])
    ws.append(["Parameter", "Value", "Description"])
    headers = ws[3]
    for cell in headers:
        cell.fill = PatternFill("solid", fgColor="1F4E79")
        cell.font = Font(color="FFFFFF", bold=True)

    params = [
        ["Baseline Conversion (%)", 5, "Current conversion rate"],
        ["MDE (%)", 1, "Minimum detectable effect"],
        ["Significance Level (α)", 0.05, "Type I error rate"],
        ["Statistical Power", 0.80, "1 - Type II error rate"],
    ]
    for row in params:
        ws.append(row)

    ws.append([])
    ws.append(["Result"])
    ws["A7"].font = Font(bold=True, size=12)

    baseline = 0.05
    mde = 0.01
    n = sample_size_proportion(baseline, mde, alpha=0.05, power=0.8)
    ws.append(["Required Sample Size per Group", n])
    ws.append(["Total Sample Size (both groups)", n * 2])
    ws.append(["Expected Lift", f"{(mde/baseline)*100:.1f}%"])

    auto_width(ws)

    # ============================================================
    # Sheet 2: Significance Tester
    # ============================================================
    ws2 = wb.create_sheet("Significance Tester")
    ws2.append(["A/B Test Significance Calculator"])
    ws2.merge_cells("A1:F1")
    ws2["A1"].font = Font(size=14, bold=True)
    ws2["A1"].alignment = Alignment(horizontal="center")

    ws2.append([])
    ws2.append(["Group", "Sample Size", "Conversions", "Conversion Rate (%)", "z-score", "p-value", "Significant?"])
    headers2 = ws2[3]
    for cell in headers2:
        cell.fill = PatternFill("solid", fgColor="1F4E79")
        cell.font = Font(color="FFFFFF", bold=True)

    # Example: Free delivery threshold test
    control_n, control_conv = 10000, 520
    treatment_n, treatment_conv = 10000, 580

    result = z_test_proportion(control_n, control_conv, treatment_n, treatment_conv)

    ws2.append([
        "Control (₹99 threshold)",
        control_n, control_conv, result["p1_pct"], "", "", ""
    ])
    ws2.append([
        "Treatment (₹49 threshold)",
        treatment_n, treatment_conv, result["p2_pct"], result["z"], result["p_value"],
        "YES ✓" if result["significant"] else "NO ✗"
    ])
    ws2.append([])
    ws2.append(["Conclusion"])
    ws2["A7"].font = Font(bold=True)
    ws2.append([f"The treatment group shows a {(result['p2_pct']-result['p1_pct']):.1f}pp lift in conversion rate."
                f" This is {'statistically significant' if result['significant'] else 'NOT statistically significant'} (p={result['p_value']})."])

    auto_width(ws2)

    # ============================================================
    # Sheet 3: Power Analysis
    # ============================================================
    ws3 = wb.create_sheet("Power Analysis")
    ws3.append(["Power Analysis — What MDE can you detect with N=10,000?"])
    ws3.merge_cells("A1:D1")
    ws3["A1"].font = Font(size=14, bold=True)
    ws3["A1"].alignment = Alignment(horizontal="center")

    ws3.append([])
    ws3.append(["Baseline (%)", "Sample per Group", "MDE Detected (pp)", "Power"])
    headers3 = ws3[3]
    for cell in headers3:
        cell.fill = PatternFill("solid", fgColor="1F4E79")
        cell.font = Font(color="FFFFFF", bold=True)

    baselines = [3, 5, 8, 10, 15]
    for bl in baselines:
        for n_per_group in [5000, 10000, 20000, 50000]:
            mde_pp = 0
            power = 0.5
            while power < 0.799:
                mde_pp += 0.1
                n = sample_size_proportion(bl / 100, mde_pp / 100, alpha=0.05, power=power)
                power = 0.8
                if n <= n_per_group:
                    break
                power += 0.01
            ws3.append([bl, n_per_group, round(mde_pp, 1), "80%"])
            break  # just one row per baseline for clarity

    auto_width(ws3)

    # ============================================================
    # Sheet 4: Pre-built Example
    # ============================================================
    ws4 = wb.create_sheet("Free Delivery Example")
    ws4.append(["Example: Free Delivery Threshold Test"])
    ws4.merge_cells("A1:D1")
    ws4["A1"].font = Font(size=14, bold=True)
    ws4["A1"].alignment = Alignment(horizontal="center")

    ws4.append([])
    ws4.append(["Hypothesis: Lowering free delivery threshold from ₹99 to ₹49 increases conversion rate"])
    ws4.append([])
    ws4.append(["Metric", "Control (₹99)", "Treatment (₹49)"])
    ws4.append(["Total Users", 10000, 10000])
    ws4.append(["Converted Users", 520, 580])
    ws4.append(["Conversion Rate", "5.2%", "5.8%"])
    ws4.append(["Absolute Lift", "+0.6pp"])
    ws4.append(["Relative Lift", "+11.5%"])
    ws4.append([])
    ws4.append(["Statistical Test: Two-proportion z-test"])
    ws4.append(["z-score", result["z"]])
    ws4.append(["p-value", result["p_value"]])
    ws4.append(["Significant at α=0.05?", "YES" if result["significant"] else "NO"])
    ws4.append([])
    ws4.append(["Recommendation: Roll out the ₹49 threshold if the 0.6pp lift justifies the delivery cost increase."])

    auto_width(ws4)

    out_path = OUTPUT_DIR / "ab_test_calculator.xlsx"
    wb.save(str(out_path))
    print(f"Saved A/B test calculator → {out_path}")


if __name__ == "__main__":
    build_ab_calculator()
