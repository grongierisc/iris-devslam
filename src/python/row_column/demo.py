from utilsrowcolumn import *
import time

# pylint: disable-all

list_tables = ["Demo.BankTransactionRow", "Demo.BankTransactionColumn","Demo.BankTransactionIndex","Demo.BankTransactionMix" ]

# init drop table if exists
print("init drop table if exists")
for table in list_tables:
    benchmark_sql_query("DROP TABLE IF EXISTS %s" % table)

# drop table description
print("drop table description")
benchmark_sql_query("DROP TABLE IF EXISTS Demo.BankTransactionDescription")

# create tables
# row storage
sql_row = """
CREATE TABLE Demo.BankTransactionRow (
  AccountNumber INTEGER,
  TransactionDate DATE,
  Description VARCHAR(100),
  Amount NUMERIC(10,2),
  Type VARCHAR(10)
)
"""

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

print("create tables")
sqls = [sql_row, sql_column, sql_index, sql_mix]
for sql in sqls:
    benchmark_sql_query(sql)

# create clonar index on amount
print("create clonar index on amount")
benchmark_sql_query("""CREATE COLUMNAR INDEX AmountIndex
ON Demo.BankTransactionIndex(Amount)""")

print("create data")
data = create_n_fake_data(100000,list_tables)

x = 100
print(f"\ninsert {x}*64 000 rows")
start = time.time()
for i in range(x):
    for table in list_tables:
        add_64000_rows(table)
end = time.time()
print(f"insert {x*64000} rows in {end - start} row per second : {64000*x/(end - start)}")

for table in list_tables:
    benchmark_sql_query(f"build index for table {table}")

# tune table
print("tune table")
for table in list_tables:
    benchmark_sql_query("TUNE TABLE %s" % table)

# create a description table of debit and credit
print("create a description table of debit and credit")
benchmark_sql_query("""
CREATE TABLE Demo.BankTransactionDescription (
    Description VARCHAR(100),
    Type VARCHAR(10)
)
"""
)

# insert data in description table
print("insert data in description table")
benchmark_sql_query("""
INSERT INTO Demo.BankTransactionDescription
values
('Salary','credit')
""")
benchmark_sql_query("""
INSERT INTO Demo.BankTransactionDescription
values
('Rent','debit')
"""
)


benchmark_sql_query('PURGE CACHED QUERIES')

# query count data
print("query count data")
for table in list_tables:
    print_sql_query(f"SELECT COUNT(*) FROM {table}")

# query data
print("query data")
for table in list_tables:
    benchmark_sql_query("SELECT TOP 100000 * FROM %s " % table)

# benchmark aggregation
print("benchmark aggregation")
for table in list_tables:
    benchmark_sql_query("SELECT AVG(ABS(Amount)) FROM %s " % table)

# benchmark join
print("benchmark join")
for table in list_tables:
    benchmark_sql_query("""SELECT TOP 100000 * FROM %s t1 
        JOIN Demo.BankTransactionDescription t2 ON t1.Type = t2.Type""" % table)

# benchmark insert
print("benchmark insert")
for table in list_tables:
    start = time.time()
    print(f"for table {table}")
    create_n_fake_data(10000,[table])
    end = time.time()
    
# table size
print("table size")
for table in list_tables:
    print_sql_query("SELECT * FROM bdb_sql.TableSize('%s')" % table)
