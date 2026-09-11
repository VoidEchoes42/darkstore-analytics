# Ground Ops Observations

First-hand field notes from shadowing/interviewing a local quick-commerce delivery team.

---

## Observation 1: Picker Bottleneck at Peak Hours

**What I saw:**
At a Blinkit dark store in Bangalore during 7-8 PM, 3 pickers were handling 120+ orders. The picking area was a narrow aisle with products stacked 6 feet high. Pickers had to climb small ladders for top-shelf items, adding 30-60 seconds per order.

**Why it matters:**
Picking delay was the #1 root cause of SLA breaches in the SQL analysis (Module 02). The data showed 62% of breach days had picking delays > 5 minutes. This observation confirms the bottleneck is physical — the store layout can't handle peak throughput.

**Data insight:**
SQL Module 06 Q6.2 shows Store #5 hitting 108% utilization at 8 PM. If picking speed improves by 20% (better layout + more pickers), breach rate could drop from 18% to ~12% during peak.

---

## Observation 2: Delivery Partner Idle Time Between Assignments

**What I saw:**
Delivery partners reported 15-25 minutes of idle time between order assignments. During this time, they wait near the store for the next dispatch call. Partners on two-wheelers can cover 2-3 km in that time but are stuck waiting.

**Why it matters:**
This idle time represents wasted capacity. If orders were batched smarter (clustering nearby deliveries), partners could handle 20-30% more orders per shift.

**Data insight:**
SQL Module 02 Q2.4 shows partner on-time rates ranging from 78% to 96%. The 78% performers are typically those who get poorly batched orders (long detours, single orders far from hub). Better batching could lift the bottom quartile to 85%+.

---

## Observation 3: "Ghost Inventory" — Products Marked In-Stock But Actually Unavailable

**What I saw:**
I saw a customer order Maggi noodles, and the picker walked to the shelf, found it empty, and had to substitute with a different brand. The system still showed 12 units in stock. The picker said this happens 10-15 times per shift during peak.

**Why it matters:**
This is a major source of SLA delays and customer dissatisfaction. Every "out of stock during picking" event adds 2-3 minutes to the order and often results in a substitution the customer doesn't want.

**Data insight:**
SQL Module 04 Q4.4 (stockout detection) can identify items with recurring stock mismatches. Implementing real-time inventory updates (scanning on shelf) could reduce picking delays by an estimated 30%.

---

## Observation 4: Rain Impact Is Amplified by Lack of Rain Gear

**What I saw:**
On a rainy evening, I observed delivery partners riding scooters without rain covers. They were slower (20-30% longer delivery times) and some orders were cancelled mid-route because partners couldn't continue in heavy rain.

**Why it matters:**
SQL Module 02 Q2.6 confirms: rain days have 8.2% higher breach rates (12.1% vs 3.9%). But the data doesn't capture the full picture — it doesn't show cancelled orders that never reached "late" status.

**Data insight:**
If rain gear + proper routing reduces rain-day breach rates from 12.1% to 8%, that's ~4,000 fewer breach events per month across 50 stores.

---

## Observation 5: Customer Communication Gap During Delays

**What I saw:**
When deliveries were running late (15+ minutes), customers had no visibility into the delay. They called the store, the store called the partner, and the information took 3-4 hops to reach the customer. This created frustration and cancellation requests.

**Why it matters:**
The Blinkit app has push notifications, but they're triggered only at certain checkpoints. There's no "your order is 10 min late" proactive notification.

**Data insight:**
Orders with delivery times > 15 minutes past SLA have 3x higher cancellation rates. If even 10% of these customers are retained via proactive notifications, that's ~₹8L/month in retained GMV.

---

## Observation 6: Early Morning Underutilization (6-8 AM)

**What I saw:**
The dark store opens at 6 AM, but only 2-3 orders come in before 8 AM. The 4 opening staff have very little to do. Yet during 7-9 PM, the same staff are overwhelmed.

**Why it matters:**
This is a staffing misalignment. The shift schedule doesn't match the demand curve.

**Data insight:**
SQL Module 01 Q1.2 (hourly heatmap) shows that 6-8 AM orders are < 5% of daily volume. A staggered shift (2 staff at 6 AM, full staff at 10 AM) could save ~₹45K/month in labor costs per store.

---

## Key Takeaway

**The data tells you *what* is broken. The ground tells you *why*.**

The biggest gap between data and reality is inventory accuracy (ghost inventory) and staffing misalignment (peak vs. idle hours). Fixing these two would reduce SLA breaches by an estimated 25-30% without adding any new technology — just better processes and shift scheduling.
