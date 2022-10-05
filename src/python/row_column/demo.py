# a demo on Taxi data to show column and row storage

import iris
import time
import csv
import random
import datetime
import string
import numpy as np

from utilsrowcolumn import *

# benchmark an sql query
def benchmark_sql_query(sql_query):
    start = time.time()
    rs= iris.sql.exec(sql_query)
    for row in rs :
        pass
    end = time.time()
    print(f"{sql_query} in {end - start}")

# print result of sql query
def print_sql_query(sql_query):
    print(f"{sql_query} :")
    rs = iris.sql.exec(sql_query)
    for row in rs:
        print(row)

# create n fake data written in a csv file with a progress bar
def create_n_fake_data(n):


    def random_string(string_length=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(string_length))

    def random_date(start, end):
        return start + datetime.timedelta(
            # Get a random amount of seconds between `start` and `end`
            seconds=random.randint(0, int((end - start).total_seconds())),
        )

    def random_amount():
        return np.random.uniform(0, 10000)

    def random_type():
        return random.choice(['credit', 'debit'])

    def random_account_number():
        return random.randint(1000000, 9999999)

    for i in range(n):
        # progress bar tqdm
        # display every 0.1%
        if i % (n // 1000) == 0:
            print(f"\r{i/n*100:.1f}%", end='')
        data = [
            random_account_number(),
            random_date(datetime.date(2018, 1, 1), datetime.date(2019, 1, 1)),
            random_string(10),
            random_amount(),
            random_type()
        ]
        for table in list_tables:
            iris.sql.exec(f"INSERT INTO {table} VALUES (?,DATE(?),?,?,?)", data[0],data[1].isoformat(),data[2],data[3],data[4])
    

list_tables = ["Demo.BankTransactionRow", "Demo.BankTransactionColumn","Demo.BankTransactionIndex","Demo.BankTransactionMix" ]

# init drop table if exists
print("init drop table if exists")
for table in list_tables:
    benchmark_sql_query("DROP TABLE IF EXISTS %s" % table)

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

# create index on type

# for table in list_tables:
#     benchmark_sql_query(f"CREATE BITMAP INDEX TypeIndex ON {table}(Type)")

# create clonar index on amount
print("create clonar index on amount")
benchmark_sql_query("""CREATE COLUMNAR INDEX AmountIndex
ON Demo.BankTransactionIndex(Amount)""")

print("create data")
data = create_n_fake_data(100000)

x = 50
print(f"\ninsert {x}*64 000 rows")
for i in range(50):
    for table in list_tables:
        add_64000_rows(table)

for table in list_tables:
    benchmark_sql_query(f"build index for table {table}")

# tune table
print("tune table")
for table in list_tables:
    benchmark_sql_query("TUNE TABLE %s" % table)

iris.sql.exec('PURGE CACHED QUERIES')

# query count data
print("query count data")
for table in list_tables:
    print_sql_query(f"SELECT COUNT(*) FROM {table}")

# query data
print("query data")
for table in list_tables:
    benchmark_sql_query("SELECT * FROM %s WHERE Amount > 5000 and Type = 'credit'" % table)

# benchmark aggregation
print("benchmark aggregation")
for table in list_tables:
    benchmark_sql_query("SELECT AVG(ABS(Amount)) FROM %s  WHERE Type = 'credit'" % table)


    
