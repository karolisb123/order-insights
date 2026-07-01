# Order Insights

A tiny, zero-dependency Python CLI for analyzing e-commerce orders from a CSV file.
Point it at your order export and get instant sales analytics, top-product rankings,
a daily revenue trend, and low-stock alerts.

Built for small online stores where a full BI tool is overkill but a spreadsheet
is getting painful.

## Features

- **Sales summary** — revenue, order count, units sold, average order value
- **Top products** by revenue
- **Daily revenue trend** rendered as a unicode sparkline right in your terminal
- **Low-stock alerts** when you supply an inventory file
- **Text report export** for sharing or archiving
- **No dependencies** — pure Python standard library

## Install

No packages to install. Just clone and run:

```bash
git clone https://github.com/YOUR_USERNAME/order-insights.git
cd order-insights
python3 -m order_insights.cli report sample_data/orders.csv
```

Or install it as a command:

```bash
pip install -e .
order-insights report sample_data/orders.csv
```

## Usage

```bash
# Basic report
python3 -m order_insights.cli report orders.csv

# With low-stock alerts and a custom threshold
python3 -m order_insights.cli report orders.csv -i inventory.csv -t 5

# Show top 10 products and export a text report
python3 -m order_insights.cli report orders.csv -n 10 -o report.txt
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-i`, `--inventory` | Path to an inventory CSV (enables low-stock alerts) | — |
| `-t`, `--threshold` | Low-stock threshold | 10 |
| `-n`, `--top` | Number of top products to show | 5 |
| `-o`, `--out` | Write a text report to this path | — |

## CSV format

**orders.csv** needs these columns:

```
order_id,date,sku,product,quantity,price
1001,2026-06-01,PKM-CHAR-01,Charizard Holo Card,2,45.00
```

**inventory.csv** (optional):

```
sku,quantity_on_hand
PKM-CHAR-01,4
```

Sample files live in [`sample_data/`](sample_data/).

## Example output

```
=== Sales Summary ===
  Revenue      $660.21
  Orders       14
  Units sold   44
  Avg order    $47.16

=== Top Products by Revenue ===
       $315.00     7 units  Charizard Holo Card [PKM-CHAR-01]
        ...

=== Daily Revenue ===
  Trend  ▆▂▄▄▁▁█

=== Low Stock (<= 5) ===
  ⚠   2 left  Card Binder [PKM-BINDER-01]
```

## Running tests

```bash
python3 -m unittest discover tests
```

## License

MIT — see [LICENSE](LICENSE).
