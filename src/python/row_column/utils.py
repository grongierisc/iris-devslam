import iris
import random
import datetime
import time
import numpy as np

def random_date(start, end):
    return start + datetime.timedelta(seconds=random.randint(0, int((end - start).total_seconds())))
def random_passenger_count():
    # passengeer_count have a distribution of 1,2,3,4,5,6 with a greater chance of 1
    return np.random.choice([1,2,3,4,5,6], p=[0.5, 0.1, 0.1, 0.1, 0.1, 0.1])
def random_trip_distance():
    return np.random.uniform(0, 100)
def random_RatecodeID():
    return np.random.choice([1,2,3,4,5,6], p=[0.1, 0.1, 0.1, 0.5, 0.1, 0.1])
def random_store_and_fwd_flag():
    return np.random.choice(['Y', 'N'], p=[0.1, 0.9])
def random_PULocationID():
    return np.random.randint(1, 263)
def random_DOLocationID():
    return np.random.randint(1, 263)
def random_payment_type():
    return np.random.choice([1,2,3], p=[0.5, 0.1, 0.4])
def random_fare_amount():
    return np.random.uniform(0, 100)
def random_extra():
    return np.random.uniform(0, 100)
def random_mta_tax():
    return np.random.uniform(0, 100)
def random_tip_amount():
    return np.random.uniform(0, 10)
def random_tolls_amount():
    return np.random.uniform(0, 10)
def random_improvement_surcharge():
    return np.random.uniform(0, 10)
def random_total_amount():
    return np.random.uniform(0, 100)

# generate 1000 rows of data
def create_fake_taxi_ride_data(n):
    data = []
    for i in range(n):
        data.append([
            random.randint(1, 2), # VendorID
            random_date(datetime.datetime(2018, 1, 1), datetime.datetime(2018, 12, 31)), # tpep_pickup_datetime
            random_date(datetime.datetime(2018, 1, 1), datetime.datetime(2018, 12, 31)), # tpep_dropoff_datetime
            random_passenger_count(), # passenger_count
            random_trip_distance(), # trip_distance
            random_RatecodeID(), # RatecodeID
            random_store_and_fwd_flag(), # store_and_fwd_flag
            random_PULocationID(), # PULocationID
            random_DOLocationID(), # DOLocationID
            random_payment_type(), # payment_type
            random_fare_amount(), # fare_amount
            random_extra(), # extra
            random_mta_tax(), # mta_tax
            random_tip_amount(), # tip_amount
            random_tolls_amount(), # tolls_amount
            random_improvement_surcharge(), # improvement_surcharge
            random_total_amount(), # total_amount
        ])
    return data

# generate a csv file
def generate_csv(data, filename):
    import csv
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def create_fake_taxi_zone_lookup():
    data = []
    for i in range(1, 263):
        data.append((i, 'Borough', 'Zone', 'service_zone'))
    return data

def sql_query(query):
    print(query)
    iris.sql.exec(query)

def benchmark_sql_query(sql_query):
    start = time.time()
    iris.sql.exec(sql_query)
    end = time.time()
    print(f"{sql_query} in {end - start}")
