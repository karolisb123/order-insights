"""Order Insights — a small CLI for analyzing e-commerce orders.

Reads a CSV of orders, prints sales analytics, flags low-stock products,
and can export a summary report. No external dependencies.
"""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def load_orders(path):
    """Load orders from a CSV file into a list of dicts."""
    orders = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"order_id", "date", "sku", "product", "quantity", "price"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
        for i, row in enumerate(reader, start=2):
            try:
                row["quantity"] = int(row["quantity"])
                row["price"] = float(row["price"])
                row["date"] = datetime.strptime(row["date"].strip(), "%Y-%m-%d").date()
            except (ValueError, KeyError) as e:
                raise ValueError(f"Bad data on line {i}: {e}") from e
            orders.append(row)
    return orders


def load_inventory(path):
    """Load current stock levels: {sku: quantity_on_hand}."""
    stock = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stock[row["sku"]] = int(row["quantity_on_hand"])
    return stock


def money(amount):
    return f"${amount:,.2f}"


def summarize(orders):
    """Return aggregate stats over all orders."""
    total_revenue = sum(o["quantity"] * o["price"] for o in orders)
    total_units = sum(o["quantity"] for o in orders)
    unique_orders = len({o["order_id"] for o in orders})
    aov = total_revenue / unique_orders if unique_orders else 0
    return {
        "revenue": total_revenue,
        "units": total_units,
        "orders": unique_orders,
        "line_items": len(orders),
        "aov": aov,
    }


def top_products(orders, n=5):
    """Return top-N products by revenue."""
    rev = defaultdict(float)
    qty = defaultdict(int)
    names = {}
    for o in orders:
        rev[o["sku"]] += o["quantity"] * o["price"]
        qty[o["sku"]] += o["quantity"]
        names[o["sku"]] = o["product"]
    ranked = sorted(rev.items(), key=lambda kv: kv[1], reverse=True)
    return [(sku, names[sku], qty[sku], rev[sku]) for sku, _ in ranked[:n]]


def revenue_by_day(orders):
    """Return {date: revenue} sorted by date."""
    by_day = defaultdict(float)
    for o in orders:
        by_day[o["date"]] += o["quantity"] * o["price"]
    return dict(sorted(by_day.items()))


def low_stock(stock, orders, threshold):
    """Flag SKUs at or below threshold. Uses order data for names."""
    names = {o["sku"]: o["product"] for o in orders}
    flagged = [
        (sku, names.get(sku, "(unknown)"), qty)
        for sku, qty in stock.items()
        if qty <= threshold
    ]
    return sorted(flagged, key=lambda t: t[2])


def sparkline(values):
    """Render a tiny unicode bar chart from a list of numbers."""
    if not values:
        return ""
    bars = "▁▂▃▄▅▆▇█"
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    return "".join(bars[int((v - lo) / span * (len(bars) - 1))] for v in values)


def cmd_report(args):
    orders = load_orders(args.orders)
    if not orders:
        print("No orders found.")
        return

    s = summarize(orders)
    print("\n=== Sales Summary ===")
    print(f"  Revenue      {money(s['revenue'])}")
    print(f"  Orders       {s['orders']}")
    print(f"  Units sold   {s['units']}")
    print(f"  Line items   {s['line_items']}")
    print(f"  Avg order    {money(s['aov'])}")

    print("\n=== Top Products by Revenue ===")
    for sku, name, qty, rev in top_products(orders, args.top):
        print(f"  {money(rev):>12}  {qty:>4} units  {name} [{sku}]")

    daily = revenue_by_day(orders)
    print("\n=== Daily Revenue ===")
    print(f"  Trend  {sparkline(list(daily.values()))}")
    print(f"  Range  {min(daily)} → {max(daily)}")

    if args.inventory:
        stock = load_inventory(args.inventory)
        flagged = low_stock(stock, orders, args.threshold)
        print(f"\n=== Low Stock (<= {args.threshold}) ===")
        if flagged:
            for sku, name, qty in flagged:
                print(f"  ⚠ {qty:>3} left  {name} [{sku}]")
        else:
            print("  All products above threshold. Nice.")

    if args.out:
        write_report(args.out, orders, s, daily)
        print(f"\nReport written to {args.out}")
    print()


def write_report(path, orders, summary, daily):
    lines = []
    lines.append("Order Insights Report")
    lines.append("=" * 40)
    lines.append(f"Revenue:    {money(summary['revenue'])}")
    lines.append(f"Orders:     {summary['orders']}")
    lines.append(f"Units:      {summary['units']}")
    lines.append(f"Avg order:  {money(summary['aov'])}")
    lines.append("")
    lines.append("Top products:")
    for sku, name, qty, rev in top_products(orders, 10):
        lines.append(f"  {money(rev):>12}  {qty:>4}u  {name} [{sku}]")
    lines.append("")
    lines.append("Daily revenue:")
    for day, rev in daily.items():
        lines.append(f"  {day}  {money(rev)}")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def build_parser():
    p = argparse.ArgumentParser(
        prog="order-insights",
        description="Analyze e-commerce orders from a CSV file.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("report", help="Print a full sales report")
    r.add_argument("orders", help="Path to orders CSV")
    r.add_argument("-i", "--inventory", help="Path to inventory CSV (enables low-stock alerts)")
    r.add_argument("-t", "--threshold", type=int, default=10, help="Low-stock threshold (default: 10)")
    r.add_argument("-n", "--top", type=int, default=5, help="How many top products to show (default: 5)")
    r.add_argument("-o", "--out", help="Write a text report to this path")
    r.set_defaults(func=cmd_report)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
