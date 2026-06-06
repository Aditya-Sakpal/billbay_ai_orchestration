-- VCORBI POC schema (6 tables)

CREATE TABLE bbz_sales_perf (
    salesperson VARCHAR(100) NOT NULL,
    `Jan` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Feb` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Mar` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Apr` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `May` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Jun` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Jul` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Aug` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Sep` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Oct` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Nov` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Dec` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Total` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    Year INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (salesperson, Year)
);

CREATE TABLE rpt_revenue (
    Department VARCHAR(100) NOT NULL,
    Year INT NOT NULL,
    `Jan` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Feb` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Mar` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Apr` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `May` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Jun` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Jul` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Aug` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Sep` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Oct` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Nov` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Dec` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    `Total` DECIMAL(12, 2) NOT NULL DEFAULT 0,
    row_bg VARCHAR(20),
    PRIMARY KEY (Department, Year)
);

CREATE TABLE rpt_aging_summary (
    Salesperson VARCHAR(100) NOT NULL,
    Customer VARCHAR(200) NOT NULL,
    CreditTerm VARCHAR(50) NOT NULL,
    CreditLimit DECIMAL(12, 2) NOT NULL DEFAULT 0,
    TotalDue DECIMAL(12, 2) NOT NULL DEFAULT 0,
    MaxAging INT NOT NULL DEFAULT 0,
    user_id INT NOT NULL,
    PRIMARY KEY (Salesperson, Customer)
);

CREATE TABLE bbx_open_invoices (
    salesperson VARCHAR(100) NOT NULL,
    partner VARCHAR(200) NOT NULL,
    number VARCHAR(50) NOT NULL,
    invoice_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    amount_paid DECIMAL(12, 2) NOT NULL DEFAULT 0,
    amount_due DECIMAL(12, 2) NOT NULL DEFAULT 0,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    days_ageing INT NOT NULL DEFAULT 0,
    name VARCHAR(10) NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (number)
);

CREATE TABLE bbz_pay (
    customer VARCHAR(200) NOT NULL,
    credit_term INT NOT NULL,
    max_aging INT NOT NULL DEFAULT 0,
    avg_pay_term_3 DECIMAL(6, 2) NOT NULL DEFAULT 0,
    avg_pay_term DECIMAL(6, 2) NOT NULL DEFAULT 0,
    credit_limit DECIMAL(12, 2) NOT NULL DEFAULT 0,
    account_balance DECIMAL(12, 2) NOT NULL DEFAULT 0,
    salesperson VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    avg_sales_3 DECIMAL(12, 2) NOT NULL DEFAULT 0,
    avg_paid_3 DECIMAL(12, 2) NOT NULL DEFAULT 0,
    temp_limit DECIMAL(12, 2) NOT NULL DEFAULT 0,
    PRIMARY KEY (customer)
);

CREATE TABLE bbz_sales_quota (
    salesperson VARCHAR(100) NOT NULL,
    so_invoiced DECIMAL(12, 2) NOT NULL DEFAULT 0,
    so_uninvoiced DECIMAL(12, 2) NOT NULL DEFAULT 0,
    so_total DECIMAL(12, 2) NOT NULL DEFAULT 0,
    month INT NOT NULL,
    year INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (salesperson, month, year)
);
