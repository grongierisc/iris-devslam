from utils import *

# # create a taxi zone lookup table
# sql_query("""
# CREATE TABLE Demo.TaxiZoneLookup (
#     LocationID INTEGER,
#     Borough VARCHAR(100),
#     Zone VARCHAR(100),
#     service_zone VARCHAR(100)
# )
# """)


# # create a table for a taxi ride
# sql_query("""
# CREATE TABLE Demo.TaxiRideRow (
#     VendorID INTEGER,
#     tpep_pickup_datetime DATE,
#     tpep_dropoff_datetime DATE,
#     passenger_count INTEGER,
#     trip_distance NUMERIC(10,2),
#     RatecodeID INTEGER,
#     store_and_fwd_flag VARCHAR(1),
#     PULocationID INTEGER,
#     DOLocationID INTEGER,
#     payment_type INTEGER,
#     fare_amount NUMERIC(10,2),
#     extra NUMERIC(10,2),
#     mta_tax NUMERIC(10,2),
#     tip_amount NUMERIC(10,2),
#     tolls_amount NUMERIC(10,2),
#     improvement_surcharge NUMERIC(10,2),
#     total_amount NUMERIC(10,2)
# )
# """)


# # create a table for a taxi ride with columnar storage
# sql_query("""
# CREATE TABLE Demo.TaxiRideColumn (
#     VendorID INTEGER,
#     tpep_pickup_datetime DATE,
#     tpep_dropoff_datetime DATE,
#     passenger_count INTEGER,
#     trip_distance NUMERIC(10,2),
#     RatecodeID INTEGER,
#     store_and_fwd_flag VARCHAR(1),
#     PULocationID INTEGER,
#     DOLocationID INTEGER,
#     payment_type INTEGER,
#     fare_amount NUMERIC(10,2),
#     extra NUMERIC(10,2),
#     mta_tax NUMERIC(10,2),
#     tip_amount NUMERIC(10,2),
#     tolls_amount NUMERIC(10,2),
#     improvement_surcharge NUMERIC(10,2),
#     total_amount NUMERIC(10,2)
# )
# WITH STORAGETYPE = COLUMNAR
# """)

# # genereate 1000000 fake taxi ride data
# data = create_fake_taxi_ride_data(1000000)

# # generate a csv file
# generate_csv(data, 'taxi_ride.csv')

tables = ['Demo.TaxiRideColumn', 'Demo.TaxiRideRow']
# load the csv file into the taxi ride table
# for table in tables:
#     benchmark_sql_query(f"""LOAD DATA FROM FILE '/opt/irisapp/data/taxi_ride.csv' INTO {table}""")

# # generate lookup data
# lookup_data = create_fake_taxi_zone_lookup()

# generate_csv(lookup_data, 'taxi_zone.csv')

# # load the csv file into the taxi zone lookup table
# benchmark_sql_query("""LOAD DATA FROM FILE '/opt/irisapp/data/taxi_zone.csv' INTO Demo.TaxiZoneLookup""")
iris.sql.exec('PURGE CACHED QUERIES')

for table in tables:
    benchmark_sql_query(f"""
            SELECT Zone, Borough, Tip FROM (
                SELECT TOP 10 PULocationID, AVG(tip_amount / fare_amount) AS Tip 
                FROM {table} 
                WHERE fare_amount > 0 
                GROUP BY PULocationID 
                ORDER BY 2 DESC ) as r
            LEFT JOIN Demo.TaxiZoneLookup z ON r.PULocationID = z.LocationID
    """)

for table in tables:
    benchmark_sql_query(f"""
        SELECT AVG(fare_amount) AS fare, AVG(tip_amount) AS tip 
            FROM {table} 
            WHERE payment_type = 1
    """)