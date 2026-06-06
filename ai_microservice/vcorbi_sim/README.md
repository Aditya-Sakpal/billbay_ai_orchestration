# vcorbi_sim

Local MySQL 8.0 simulator for VCORBI read-only queries during POC development.

## Start

From this directory:

```bash
docker compose up -d
```

The container `vcorbi_sim` exposes MySQL on **host port 3307**. Init scripts in `init/` run automatically on first boot.

## Connection string

Use this in the vlang `.env` file:

```
VCORBI_URL=mysql+mysqlclient://bbai_reader:bbai_reader_pass@localhost:3307/vcorbi
```

Credentials:

| Setting  | Value              |
|----------|--------------------|
| Host     | `localhost`        |
| Port     | `3307`             |
| Database | `vcorbi`           |
| User     | `bbai_reader`      |
| Password | `bbai_reader_pass` |

## Swap to real VCORBI

Point `VCORBI_URL` in `.env` at the production read-only endpoint. No code changes are required — `app/vcorbi.py` reads the URL from settings.

## Verify

```bash
docker exec -it vcorbi_sim mysql -u bbai_reader -pbbai_reader_pass vcorbi -e "SELECT salesperson, Total FROM bbz_sales_perf LIMIT 5;"
```

Expected output includes four salespersons for Year 2026: Aelina Senitro, Louis Teo, Karen Ku, and Elaine Yeo.

## Tables (POC scope)

| Table               | Description                          |
|---------------------|--------------------------------------|
| `bbz_sales_perf`    | Monthly sales performance by rep     |
| `rpt_revenue`       | Department revenue rollup            |
| `rpt_aging_summary` | AR aging by customer                 |
| `bbx_open_invoices` | Open invoice detail                  |
| `bbz_pay`           | Customer payment behaviour           |
| `bbz_sales_quota`   | Sales order quota by month           |

## Reset data

To re-run init scripts, remove the volume and start fresh:

```bash
docker compose down -v
docker compose up -d
```
