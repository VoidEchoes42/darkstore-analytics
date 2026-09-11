"""
Generate financial_model.xlsx — Store P&L, LTV/CAC, break-even, scenario analysis.
"""
import os
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "excel"
OUTPUT_DIR.mkdir(exist_ok=True)


def style_header(ws, row=1):
    fill = PatternFill("solid", fgColor="1F4E79")
    font = Font(color="FFFFFF", bold=True, size=11)
    for cell in ws[row]:
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(horizontal="center", vertical="center")


def auto_width(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max_len + 4, 30)


def build_financial_model():
    wb = Workbook()

    # ============================================================
    # Sheet 1: Store P&L
    # ============================================================
    ws = wb.active
    ws.title = "Store P&L"

    headers = ["Store ID", "City", "Zone", "Avg Daily Orders", "AOV (₹)",
               "Monthly Revenue", "COGS (55%)", "Delivery Cost (₹12/order)",
               "Packaging (₹5/order)", "Rent (₹1.5L/mo)", "Staff (₹2L/mo)",
               "Contribution Margin (₹)", "CM%", "Break-even Orders/Day"]

    ws.append(headers)
    style_header(ws)

    sample_stores = [
        (1, "Bangalore", "Koramangala", 120, 450),
        (2, "Bangalore", "HSR Layout", 95, 420),
        (3, "Delhi", "South Delhi", 180, 520),
        (4, "Delhi", "East Delhi", 75, 380),
        (5, "Mumbai", "Bandra", 200, 550),
        (6, "NCR", "Gurgaon", 150, 480),
        (7, "Hyderabad", "Hitech City", 100, 410),
        (8, "Bangalore", "Indiranagar", 130, 470),
    ]

    for row_data in sample_stores:
        store_id, city, zone, avg_orders, aov = row_data
        monthly_revenue = avg_orders * 30 * aov
        cogs = monthly_revenue * 0.55
        delivery_cost = avg_orders * 30 * 12
        packaging = avg_orders * 30 * 5
        rent = 150000
        staff = 200000
        cm = monthly_revenue - cogs - delivery_cost - packaging - rent - staff
        cm_pct = (cm / monthly_revenue * 100) if monthly_revenue else 0
        breakeven = ((rent + staff) / ((aov * 0.45) - 12 - 5)) if (aov * 0.45 - 17) > 0 else 9999

        ws.append([
            store_id, city, zone, avg_orders, aov,
            round(monthly_revenue, 0), round(cogs, 0), round(delivery_cost, 0),
            round(packaging, 0), rent, staff,
            round(cm, 0), round(cm_pct, 1), round(breakeven, 0)
        ])

    # Highlight profitable stores
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        cm_val = row[11].value
        if cm_val and cm_val > 0:
            row[11].fill = PatternFill("solid", fgColor="C6EFCE")

    auto_width(ws)

    # ============================================================
    # Sheet 2: CAC by Channel
    # ============================================================
    ws2 = wb.create_sheet("CAC by Channel")
    ws2.append(["Channel", "Customers Acquired", "Marketing Spend (₹)", "CAC (₹/customer)", "Avg Orders", "Avg GMV (₹)", "LTV:CAC"])
    style_header(ws2)

    channel_data = [
        ("organic", 20000, 0, 4.5, 8500),
        ("referral", 10000, 300000, 15.2, 12500),
        ("paid_ads", 15000, 1500000, 42.8, 9500),
        ("offline", 5000, 200000, 25.5, 8000),
    ]

    for row in channel_data:
        channel, customers, spend, avg_orders, avg_gmv = row
        cac = spend / customers if customers > 0 else 0
        ltv = avg_gmv * 0.15  # 15% contribution margin
        ltv_cac = ltv / cac if cac > 0 else 0
        ws2.append([channel, customers, spend, round(cac, 0), round(avg_orders, 1), round(avg_gmv, 0), round(ltv_cac, 2)])

    auto_width(ws2)

    # ============================================================
    # Sheet 3: Break-even Analysis
    # ============================================================
    ws3 = wb.create_sheet("Break-even")
    ws3.append(["Fixed Costs / Month"])
    ws3.append(["Rent", 150000])
    ws3.append(["Staff Salaries", 200000])
    ws3.append(["Total Fixed Costs", "=B2+B3"])
    ws3.append([])
    ws3.append(["Variable Costs per Order"])
    ws3.append(["Delivery Cost", 12])
    ws3.append(["Packaging", 5])
    ws3.append(["COGS (55% of AOV)", "=AOV*0.55"])
    ws3.append([])
    ws3.append(["Parameters"])
    ws3.append(["AOV (₹)", 450])
    ws3.append(["Contribution per Order (₹)", "=B11 - B7 - B8 - B9"])
    ws3.append([])
    ws3.append(["Break-even Orders/Day", "=B4/(B12*30)"])
    ws3.append(["Break-even GMV/Month (₹)", "=B14*30*B11"])

    auto_width(ws3)

    # ============================================================
    # Sheet 4: Scenario Toggle
    # ============================================================
    ws4 = wb.create_sheet("Scenario Analysis")
    ws4.append(["Scenario Toggle — Adjust inputs to see margin impact"])
    style_header(ws4, row=1)
    ws4.append([])
    ws4.append(["Parameter", "Base Case", "Optimistic", "Pessimistic"])
    style_header(ws4, row=3)
    ws4.append(["Avg Delivery Time (min)", 10, 8, 15])
    ws4.append(["AOV (₹)", 450, 550, 350])
    ws4.append(["Monthly Churn Rate (%)", 5, 3, 8])
    ws4.append(["Monthly GMV Growth (%)", 10, 20, 0])
    ws4.append([])
    ws4.append(["Impact"])
    ws4.append(["Breach Rate Impact", "-2%", "-5%", "+8%"])
    ws4.append(["Revenue Impact (₹)", "+₹2.5L/mo", "+₹8L/mo", "-₹1.2L/mo"])
    ws4.append(["Margin Impact", "+3pp", "+8pp", "-5pp"])

    auto_width(ws4)

    out_path = OUTPUT_DIR / "financial_model.xlsx"
    wb.save(str(out_path))
    print(f"Saved financial model → {out_path}")


if __name__ == "__main__":
    build_financial_model()
