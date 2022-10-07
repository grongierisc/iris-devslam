from utilsrowcolumn import *

list_tables = ["Demo.BankTransactionRow", "Demo.BankTransactionColumn","Demo.BankTransactionIndex","Demo.BankTransactionMix" ]

# init drop table if exists
print("init drop table if exists")
for table in list_tables:
    benchmark_sql_query("DROP TABLE IF EXISTS %s" % table)

sql_row = """
CREATE TABLE Demo.BankTransactionRow (
  AccountNumber INTEGER,
  TransactionDate DATE,
  Description VARCHAR(100),
  Amount NUMERIC(10,2),
  Type VARCHAR(10)
)
"""
print_sql_query(sql_row)

# index column storage
sql_index = """
CREATE TABLE Demo.BankTransactionIndex (
  AccountNumber INTEGER,
  TransactionDate DATE,
  Description VARCHAR(100),
  Amount NUMERIC(10,2),
  Type VARCHAR(10)
)
"""
print_sql_query(sql_index)
# Create the index
print_sql_query("""CREATE COLUMNAR INDEX AmountIndex
ON Demo.BankTransactionIndex(Amount)""")

# column storage
sql_column = """
CREATE TABLE Demo.BankTransactionColumn (
  AccountNumber INTEGER,
  TransactionDate DATE,
  Description VARCHAR(100),
  Amount NUMERIC(10,2),
  Type VARCHAR(10)
)
WITH STORAGETYPE = COLUMNAR
"""
benchmark_sql_query(sql_column)

# mix storage
sql_mix = """
CREATE TABLE Demo.BankTransactionMix (
  AccountNumber INTEGER,
  TransactionDate DATE,
  Description VARCHAR(100),
  Amount NUMERIC(10,2) WITH STORAGETYPE = COLUMNAR,
  Type VARCHAR(10)
)
"""
benchmark_sql_query(sql_mix)

print("create data")
create_n_fake_data(64000,10,list_tables)