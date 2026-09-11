"""
Generate ops_dashboard_template.xlsx — Pivot table + slicers for orders data.
"""
import os
import numpy as np
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, LineChart, Reference, PieChart
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "excel"
OUTPUT_DIR.mkdir(exist_ok=True)


def build_ops_dashboard():
    wb = Workbook()

    # ============================================================
    # Sheet 1: Raw Data (sample)
    # ============================================================
    ws_raw = wb.active
    ws_raw.title = "Orders Data"
    headers = ["order_id", "store_id", "city", "zone", "category",
               "order_date", "hour", "gmv", "order_status", "delivery_min", "partner_id"]
    ws_raw.append(headers)

    sample_rows = [
        [1, 1, "Bangalore", "Koramangala", "Snacks", "2024-06-15", 19, 520, "delivered", 12, 45],
        [2, 3, "Delhi", "South Delhi", "Beverages", "2024-06-15", 20, 380, "delivered", 15, 120],
        [3, 5, "Mumbai", "Bandra", "Dairy", "2024-06-15", 18, 450, "delivered", 8, 200],
        [4, 1, "Bangalore", "Koramangala", "Grocery", "2024-06-16", 19, 680, "delivered", 10, 45],
        [5, 6, "NCR", "Gurgaon", "Personal Care", "2024-06-16", 20, 290, "delivered", 18, 50],
        [6, 2, "Bangalore", "HSR Layout", "Bakery", "2024-06-16", 18, 420, "delivered", 11, 75],
        [7, 3, "Delhi", "South Delhi", "Fruits & Vegetables", "2024-06-17", 19, 550, "delivered", 9, 120],
        [8, 5, "Mumbai", "Bandra", "Household", "2024-06-17", 20, 310, "delivered", 22, 200],
    ]
    for row in sample_rows:
        ws_raw.append(row)

    auto_width(ws_raw)

    # ============================================================
    # Sheet 2: Pivot — Daily GMV by Store
    # ============================================================
    ws_pivot = wb.create_sheet("Daily GMV by Store")
    ws_pivot.append(["Store ID", "City", "Zone", "Total Orders", "Total GMV (₹)", "Avg AOV (₹)", "Fulfillment Rate (%)"])

    pivot_data = [
        [1, "Bangalore", "Koramangala", 3240, 1458000, 450, 97.5],
        [2, "Bangalore", "HSR Layout", 2850, 1197000, 420, 96.2],
        [3, "Delhi", "South Delhi", 5400, 2808000, 520, 94.8],
        [4, "Delhi", "East Delhi", 2250, 855000, 380, 93.5],
        [5, "Mumbai", "Bandra", 6000, 3300000, 550, 95.1],
        [6, "NCR", "Gurgaon", 4500, 2160000, 480, 96.8],
        [7, "Hyderabad", "Hitech City", 3000, 1230000, 410, 97.2],
        [8, "Bangalore", "Indiranagar", 3900, 1833000, 470, 95.6],
    ]
    for row in pivot_data:
        ws_pivot.append(row)

    auto_width(ws_pivot)

    # Chart
    chart = BarChart()
    chart.type = "col"
    chart.title = "Total GMV by Store"
    chart.y_axis.title = "GMV (₹)"
    chart.x_axis.title = "Store ID"

    data_ref = Reference(ws_pivot, min_col=5, min_row=1, max_row=9)
    cats = Reference(ws_pivot, min_col=1, min_row=2, max_row=9)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats)
    ws_pivot.add_chart(chart, "I2")

    # ============================================================
    # Sheet 3: Category Mix
    # ============================================================
    ws_cat = wb.create_sheet("Category Mix")
    ws_cat.append(["Category", "Orders", "Revenue (₹)", "% of Total"])
    cat_data = [
        ["Snacks", 180000, 45000000, 16.2],
        ["Beverages", 150000, 37500000, 13.5],
        ["Dairy", 120000, 30000000, 10.8],
        ["Grocery & Staples", 250000, 50000000, 18.0],
        ["Personal Care", 100000, 25000000, 9.0],
        ["Household", 90000, 18000000, 6.5],
        ["Fruits & Vegetables", 80000, 20000000, 7.2],
        ["Bakery", 70000, 14000000, 5.0],
        ["Others", 150000, 30000000, 10.8],
    ]
    for row in cat_data:
        ws_cat.append(row)

    auto_width(ws_cat)

    pie_chart = PieChart()
    pie_chart.title = "Revenue by Category"
    labels_ref = Reference(ws_cat, min_col=1, min_row=2, max_row=10)
    data_ref2 = Reference(ws_cat, min_col=3, min_row=1, max_row=10)
    pie_chart.add_data(data_ref2, titles_from_data=True)
    pie_chart.set_categories(labels_ref)
    ws_cat.add_chart(pie_chart, "F2")

    # ============================================================
    # Sheet 4: SLA Trend
    # ============================================================
    ws_sla = wb.create_sheet("SLA Trend")
    ws_sla.append(["Date", "Total Orders", "Late Orders", "Breach Rate (%)", "Avg Delivery (min)"])
    sla_data = []
    from datetime import date, timedelta
    d = date(2024, 6, 1)
    for i in range(30):
        breach = np.random.uniform(3, 7)
        total = np.random.randint(30000, 50000)
        late = int(total * breach / 100)
        ws_sla.append([d.isoformat(), total, late, round(breach, 1), round(np.random.uniform(8, 14), 1)])
        d += timedelta(days=1)

    auto_width(ws_sla)

    line_chart = LineChart()
    line_chart.title = "SLA Breach Rate Trend"
    line_chart.y_axis.title = "Breach Rate (%)"
    line_chart.x_axis.title = "Date"
    data_ref3 = Reference(ws_sla, min_col=4, min_row=1, max_row=31)
    line_chart.add_data(data_ref3, titles_from_data=True)
    ws_sla.add_chart(line_chart, "G2")

    out_path = OUTPUT_DIR / "ops_dashboard_template.xlsx"
    wb.save(str(out_path))
    print(f"Saved ops dashboard template → {out_path}")


def auto_width(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max_len + 4, 30)



if __name__ == "__main__":
    build_ops_dashboard()
