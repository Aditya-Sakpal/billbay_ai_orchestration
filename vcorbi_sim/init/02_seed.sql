-- Synthetic POC data for Singapore beverages distributor (SGD, Year 2026)
-- Salespersons: Aelina Senitro (42), Louis Teo (43), Karen Ku (44), Elaine Yeo (45)

-- ---------------------------------------------------------------------------
-- bbz_sales_perf — monthly sales by salesperson (Jan–May populated, Jun–Dec = 0)
-- ---------------------------------------------------------------------------
INSERT INTO bbz_sales_perf (salesperson, `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`, `Total`, Year, user_id) VALUES
('Aelina Senitro',  82500.00,  91200.00,  88750.00,  95400.00, 102300.00, 0, 0, 0, 0, 0, 0, 0, 460150.00, 2026, 42),
('Louis Teo',       67800.00,  72100.00,  69500.00,  74200.00,  78900.00, 0, 0, 0, 0, 0, 0, 0, 362500.00, 2026, 43),
('Karen Ku',        54300.00,  58900.00,  61200.00,  63400.00,  67100.00, 0, 0, 0, 0, 0, 0, 0, 304900.00, 2026, 44),
('Elaine Yeo',      48900.00,  51200.00,  53800.00,  55600.00,  58400.00, 0, 0, 0, 0, 0, 0, 0, 267900.00, 2026, 45);

-- ---------------------------------------------------------------------------
-- rpt_revenue — department-level revenue rollup
-- ---------------------------------------------------------------------------
INSERT INTO rpt_revenue (Department, Year, `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`, `Total`, row_bg) VALUES
('Beverages - On Trade',   2026, 128400.00, 136200.00, 141500.00, 148600.00, 155800.00, 0, 0, 0, 0, 0, 0, 0, 710500.00, '#E8F4FD'),
('Beverages - Off Trade', 2026,  89200.00,  94500.00,  97800.00, 101200.00, 106400.00, 0, 0, 0, 0, 0, 0, 0, 489100.00, '#FDF6E8'),
('Beverages - Corporate', 2026,  35700.00,  38200.00,  40150.00,  42400.00,  44600.00, 0, 0, 0, 0, 0, 0, 0, 201050.00, '#F0FDF4'),
('Total Revenue',          2026, 253300.00, 268900.00, 279450.00, 292200.00, 306800.00, 0, 0, 0, 0, 0, 0, 0, 1400650.00, '#E5E7EB');

-- ---------------------------------------------------------------------------
-- rpt_aging_summary — AR aging by customer (≥3 with MaxAging > 0)
-- ---------------------------------------------------------------------------
INSERT INTO rpt_aging_summary (Salesperson, Customer, CreditTerm, CreditLimit, TotalDue, MaxAging, user_id) VALUES
('Aelina Senitro', 'Marina Bay Hotels Pte Ltd',      '30 days', 150000.00,  42500.00,  45, 42),
('Aelina Senitro', 'Orchard Beverage Supplies',      '30 days',  80000.00,  18200.00,  62, 42),
('Aelina Senitro', 'Raffles Hospitality Group',        '60 days', 200000.00,  67800.00,  38, 42),
('Aelina Senitro', 'Changi Airport F&B Concessions', '30 days', 120000.00,      0.00,   0, 42),
('Louis Teo',      'Jurong Food & Beverage Co',      '30 days',  60000.00,  12400.00,  33, 43),
('Louis Teo',      'Tampines Wholesale Mart',        '60 days',  90000.00,  28700.00,  71, 43),
('Louis Teo',      'East Coast Catering Services',   '30 days',  45000.00,      0.00,   0, 43),
('Karen Ku',       'Woodlands Supermart Chain',      '90 days', 110000.00,  35200.00,  95, 44),
('Karen Ku',       'Sembawang Beverage Distributors','30 days',  55000.00,   8900.00,  28, 44),
('Karen Ku',       'Yishun Community Club Canteen',  '30 days',  25000.00,      0.00,   0, 44),
('Elaine Yeo',     'Sentosa Resort Partners',        '60 days', 175000.00,  54300.00,  52, 45),
('Elaine Yeo',     'Harbourfront Restaurant Group',  '30 days',  70000.00,  15600.00,  41, 45),
('Elaine Yeo',     'VivoCity Food Court Operators',  '30 days',  40000.00,      0.00,   0, 45);

-- ---------------------------------------------------------------------------
-- bbx_open_invoices — open invoice detail
-- ---------------------------------------------------------------------------
INSERT INTO bbx_open_invoices (salesperson, partner, number, invoice_amount, amount_paid, amount_due, invoice_date, due_date, days_ageing, name, user_id) VALUES
('Aelina Senitro', 'Marina Bay Hotels Pte Ltd',      'INV-2026-0142', 28500.00,  8500.00, 20000.00, '2026-03-15', '2026-04-14',  52, 'SGD', 42),
('Aelina Senitro', 'Marina Bay Hotels Pte Ltd',      'INV-2026-0187', 22500.00,     0.00, 22500.00, '2026-04-02', '2026-05-02',  35, 'SGD', 42),
('Aelina Senitro', 'Orchard Beverage Supplies',      'INV-2026-0203', 18200.00,     0.00, 18200.00, '2026-02-28', '2026-03-30',  62, 'SGD', 42),
('Aelina Senitro', 'Raffles Hospitality Group',      'INV-2026-0256', 45200.00, 12000.00, 33200.00, '2026-04-10', '2026-06-09',  27, 'SGD', 42),
('Aelina Senitro', 'Raffles Hospitality Group',      'INV-2026-0311', 34600.00,     0.00, 34600.00, '2026-05-05', '2026-07-04',   2, 'SGD', 42),
('Louis Teo',      'Jurong Food & Beverage Co',    'INV-2026-0098', 12400.00,     0.00, 12400.00, '2026-04-18', '2026-05-18',  19, 'SGD', 43),
('Louis Teo',      'Tampines Wholesale Mart',        'INV-2026-0165', 18900.00,  5200.00, 13700.00, '2026-03-01', '2026-05-01',  71, 'SGD', 43),
('Louis Teo',      'Tampines Wholesale Mart',        'INV-2026-0229', 15000.00,     0.00, 15000.00, '2026-04-22', '2026-06-21',  15, 'SGD', 43),
('Karen Ku',       'Woodlands Supermart Chain',      'INV-2026-0076', 22100.00,     0.00, 22100.00, '2026-02-10', '2026-05-11',  95, 'SGD', 44),
('Karen Ku',       'Woodlands Supermart Chain',      'INV-2026-0194', 13100.00,     0.00, 13100.00, '2026-04-05', '2026-07-04',  32, 'SGD', 44),
('Karen Ku',       'Sembawang Beverage Distributors','INV-2026-0241',  8900.00,     0.00,  8900.00, '2026-05-01', '2026-05-31',   6, 'SGD', 44),
('Elaine Yeo',     'Sentosa Resort Partners',        'INV-2026-0112', 31200.00,  8400.00, 22800.00, '2026-03-20', '2026-05-19',  47, 'SGD', 45),
('Elaine Yeo',     'Sentosa Resort Partners',        'INV-2026-0278', 31500.00,     0.00, 31500.00, '2026-04-28', '2026-06-27',  23, 'SGD', 45),
('Elaine Yeo',     'Harbourfront Restaurant Group',  'INV-2026-0295', 15600.00,     0.00, 15600.00, '2026-04-15', '2026-05-15',  22, 'SGD', 45);

-- ---------------------------------------------------------------------------
-- bbz_pay — customer payment behaviour (30/60/90 day terms, some overdue)
-- ---------------------------------------------------------------------------
INSERT INTO bbz_pay (customer, credit_term, max_aging, avg_pay_term_3, avg_pay_term, credit_limit, account_balance, salesperson, user_id, avg_sales_3, avg_paid_3, temp_limit) VALUES
('Marina Bay Hotels Pte Ltd',       30,  62, 38.50, 35.20, 150000.00,  42500.00, 'Aelina Senitro', 42, 28500.00, 19200.00, 150000.00),
('Orchard Beverage Supplies',       30,  62, 45.00, 42.80,  80000.00,  18200.00, 'Aelina Senitro', 42, 12400.00,  8100.00,  80000.00),
('Raffles Hospitality Group',       60,  38, 52.30, 48.60, 200000.00,  67800.00, 'Aelina Senitro', 42, 35600.00, 22400.00, 200000.00),
('Changi Airport F&B Concessions',  30,   0, 28.00, 27.50, 120000.00,      0.00, 'Aelina Senitro', 42, 18900.00, 18900.00, 120000.00),
('Jurong Food & Beverage Co',       30,  33, 32.00, 30.50,  60000.00,  12400.00, 'Louis Teo',      43,  9800.00,  7200.00,  60000.00),
('Tampines Wholesale Mart',         60,  71, 58.00, 55.40,  90000.00,  28700.00, 'Louis Teo',      43, 14200.00,  9100.00,  90000.00),
('East Coast Catering Services',    30,   0, 26.50, 25.80,  45000.00,      0.00, 'Louis Teo',      43,  7600.00,  7600.00,  45000.00),
('Woodlands Supermart Chain',       90,  95, 72.00, 68.30, 110000.00,  35200.00, 'Karen Ku',       44, 16800.00, 10200.00, 110000.00),
('Sembawang Beverage Distributors', 30,  28, 31.00, 29.70,  55000.00,   8900.00, 'Karen Ku',       44,  5400.00,  4200.00,  55000.00),
('Yishun Community Club Canteen',   30,   0, 24.00, 23.50,  25000.00,      0.00, 'Karen Ku',       44,  3200.00,  3200.00,  25000.00),
('Sentosa Resort Partners',         60,  52, 48.00, 46.20, 175000.00,  54300.00, 'Elaine Yeo',     45, 22100.00, 14800.00, 175000.00),
('Harbourfront Restaurant Group',   30,  41, 36.00, 34.50,  70000.00,  15600.00, 'Elaine Yeo',     45,  8900.00,  6100.00,  70000.00),
('VivoCity Food Court Operators',   30,   0, 27.00, 26.80,  40000.00,      0.00, 'Elaine Yeo',     45,  6500.00,  6500.00,  40000.00);

-- ---------------------------------------------------------------------------
-- bbz_sales_quota — sales order quota tracking (Jan–May 2026)
-- ---------------------------------------------------------------------------
INSERT INTO bbz_sales_quota (salesperson, so_invoiced, so_uninvoiced, so_total, month, year, user_id) VALUES
('Aelina Senitro',  82500.00,  5200.00,  87700.00,  1, 2026, 42),
('Aelina Senitro',  91200.00,  3800.00,  95000.00,  2, 2026, 42),
('Aelina Senitro',  88750.00,  6100.00,  94850.00,  3, 2026, 42),
('Aelina Senitro',  95400.00,  4500.00,  99900.00,  4, 2026, 42),
('Aelina Senitro', 102300.00,  7200.00, 109500.00,  5, 2026, 42),
('Louis Teo',       67800.00,  4100.00,  71900.00,  1, 2026, 43),
('Louis Teo',       72100.00,  2900.00,  75000.00,  2, 2026, 43),
('Louis Teo',       69500.00,  5200.00,  74700.00,  3, 2026, 43),
('Louis Teo',       74200.00,  3600.00,  77800.00,  4, 2026, 43),
('Louis Teo',       78900.00,  4800.00,  83700.00,  5, 2026, 43),
('Karen Ku',        54300.00,  3200.00,  57500.00,  1, 2026, 44),
('Karen Ku',        58900.00,  2100.00,  61000.00,  2, 2026, 44),
('Karen Ku',        61200.00,  3800.00,  65000.00,  3, 2026, 44),
('Karen Ku',        63400.00,  2900.00,  66300.00,  4, 2026, 44),
('Karen Ku',        67100.00,  4100.00,  71200.00,  5, 2026, 44),
('Elaine Yeo',      48900.00,  2800.00,  51700.00,  1, 2026, 45),
('Elaine Yeo',      51200.00,  1900.00,  53100.00,  2, 2026, 45),
('Elaine Yeo',      53800.00,  3400.00,  57200.00,  3, 2026, 45),
('Elaine Yeo',      55600.00,  2500.00,  58100.00,  4, 2026, 45),
('Elaine Yeo',      58400.00,  3600.00,  62000.00,  5, 2026, 45);
