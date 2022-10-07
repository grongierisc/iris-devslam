import iris
import time
import random
import datetime
import string
import numpy as np

# pylint: disable-all

def duplicate_rows(count,table_name: str):

    if (table_name == "Demo.BankTransactionColumn"):

        g = iris.gref("^CATa.BJqo.1")

    elif (table_name == "Demo.BankTransactionIndex"):

        g = iris.gref("^CATa.C4g3.1")

    elif (table_name == "Demo.BankTransactionMix"):

        g = iris.gref("^CATa.CfQt.1")

    elif (table_name == "Demo.BankTransactionRow"): # row storage
        g = iris.gref("^CATa.BArF.1")

    else:
        print("Table name not found")
        return

    max = g[None]
    if count >= 64000:
        count = 64000

    for i in range(count):
        g[max+i+1]=g[i+1]

    g[None] = max+count

    if table_name == "Demo.BankTransactionColumn":
        iris.cls('RowColumn.Utils').AppendLastVector()
    if table_name == "Demo.BankTransactionMix":
        iris.cls('RowColumn.Utils').AppendLastVectorMix()
    


# benchmark an sql query
def benchmark_sql_query(sql_query):
    start = time.time()
    rs= iris.sql.exec(sql_query)
    i = 0
    for row in rs :
        i=i+1
    end = time.time()
    print(f"number of rows : {i}")
    print(f"{sql_query} in {end - start:.2f} seconds, row per second : {(i)/(end - start):,.2f}")

# print result of sql query
def print_sql_query(sql_query):
    print(f"{sql_query} :")
    rs = iris.sql.exec(sql_query)
    for row in rs:
        print(row)

def run_sql_query(sql_query):
    rs = iris.sql.exec(sql_query)
    for row in rs:
        print(row)

# create n fake data written in a csv file with a progress bar
def create_n_fake_data(n,m,list_tables):

    if n<64000 and m>0:
        raise Exception("n must be greater than 64000 to run duplicate_rows")

    def random_string():
        """Generate a random string 
            based on a list of words
        """
        words = ['Rent', 'Salary', 'Food', 'Clothes', 'Car', 'Phone', 'Internet', 'Insurance', 'Other',None]
        return random.choice(words)

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
        return random.randint(1000000, 1001000)

    x = 0
    start = time.time()
    for i in range(n):
        # progress bar tqdm
        # display every 0.1%
        if i % (n // 1000) == 0:
            print(f"\r{(i+1)/n*100:.1f}%", end='')
        data = [
            random_account_number(),
            random_date(datetime.date(2018, 1, 1), datetime.date(2019, 1, 1)),
            random_string(),
            random_amount(),
            random_type()
        ]
        for table in list_tables:
            x=x+1
            iris.sql.exec(f"INSERT INTO {table} VALUES (?,DATE(?),?,?,?)", data[0],data[1].isoformat(),data[2],data[3],data[4])
    end = time.time()        
    print(f"\ncreated {x:,} fake data in {end - start:.2f} seconds, number of rows per second : {x/(end - start):,.2f}")

    if m>0:
        start = time.time()
        for i in range(m):
            print(f"\r{(i+1)/m*100:.1f}%", end='')
            for table in list_tables:
                duplicate_rows(n,table)

        
            # build index
            print("build index")
            for table in list_tables:
                run_sql_query(f"build index for table {table}")
            # tune table
            print("tune table")
            for table in list_tables:
                run_sql_query("TUNE TABLE %s" % table)

        end = time.time()
        print(f"\nduplicated a total of {m*n*len(list_tables):,} rows in {end - start:.2f} row per second : {(m*n*len(list_tables))/(end - start):,.2f}")

def create_join_table():
    # create a description table of debit and credit
    print("create a description table of debit and credit")
    run_sql_query("""
    CREATE TABLE Demo.BankTransactionDescription (
        Description VARCHAR(100),
        Type VARCHAR(10)
    )
    """
    )

    # insert data in description table
    print("insert data in description table")
    run_sql_query("""
    INSERT INTO Demo.BankTransactionDescription
    values
    ('Salary','credit')
    """)
    run_sql_query("""
    INSERT INTO Demo.BankTransactionDescription
    values
    ('Rent','debit')
    """
    )