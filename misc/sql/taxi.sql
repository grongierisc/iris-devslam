-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
-- File: /tmp/Sample.sql
-- IRIS SQL DDL Export
-- Date: 27 Sep 2022 09:10:40
-- Export of: TABLES/VIEWS
-- From Namespace: IRISAPP
-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

-- Export of all Definitions for schema 'NYTaxi' --

CREATE TABLE NYTaxi.Rides(
    VendorID                 INTEGER,
    tpep_pickup_datetime     TIMESTAMP,
    tpep_dropoff_datetime    TIMESTAMP,
    passenger_count          INTEGER,
    trip_distance            DOUBLE,
    RatecodeID               INTEGER,
    store_and_fwd_flag       VARCHAR(25),
    PULocationID             INTEGER,
    DOLocationID             INTEGER,
    payment_type             INTEGER,
    fare_amount              DOUBLE,
    extra                    DOUBLE,
    mta_tax                  DOUBLE,
    tip_amount               DOUBLE,
    tolls_amount             DOUBLE,
    improvement_surcharge    DOUBLE,
    total_amount             DOUBLE,
    congestion_surcharge     DOUBLE
)
WITH
    STORAGETYPE = columnar
GO

CREATE INDEX _CDM_DOLocationID ON NYTaxi.Rides(DOLocationID)
GO

CREATE INDEX _CDM_PULocationID ON NYTaxi.Rides(PULocationID)
GO

CREATE INDEX _CDM_RatecodeID ON NYTaxi.Rides(RatecodeID)
GO

CREATE INDEX _CDM_VendorID ON NYTaxi.Rides(VendorID)
GO

CREATE INDEX _CDM_congestionsurcharge ON NYTaxi.Rides(congestion_surcharge)
GO

CREATE INDEX _CDM_extra ON NYTaxi.Rides(extra)
GO

CREATE INDEX _CDM_fareamount ON NYTaxi.Rides(fare_amount)
GO

CREATE INDEX _CDM_improvementsurcharge ON NYTaxi.Rides(improvement_surcharge)
GO

CREATE INDEX _CDM_mtatax ON NYTaxi.Rides(mta_tax)
GO

CREATE INDEX _CDM_passengercount ON NYTaxi.Rides(passenger_count)
GO

CREATE INDEX _CDM_paymenttype ON NYTaxi.Rides(payment_type)
GO

CREATE INDEX _CDM_storeandfwdflag ON NYTaxi.Rides(store_and_fwd_flag)
GO

CREATE INDEX _CDM_tipamount ON NYTaxi.Rides(tip_amount)
GO

CREATE INDEX _CDM_tollsamount ON NYTaxi.Rides(tolls_amount)
GO

CREATE INDEX _CDM_totalamount ON NYTaxi.Rides(total_amount)
GO

CREATE INDEX _CDM_tpepdropoffdatetime ON NYTaxi.Rides(tpep_dropoff_datetime)
GO

CREATE INDEX _CDM_tpeppickupdatetime ON NYTaxi.Rides(tpep_pickup_datetime)
GO

CREATE INDEX _CDM_tripdistance ON NYTaxi.Rides(trip_distance)
GO

CREATE TABLE NYTaxi.RowRides(
    VendorID                 INTEGER,
    tpep_pickup_datetime     TIMESTAMP,
    tpep_dropoff_datetime    TIMESTAMP,
    passenger_count          INTEGER,
    trip_distance            DOUBLE,
    RatecodeID               INTEGER,
    store_and_fwd_flag       VARCHAR(25),
    PULocationID             INTEGER,
    DOLocationID             INTEGER,
    payment_type             INTEGER,
    fare_amount              DOUBLE,
    extra                    DOUBLE,
    mta_tax                  DOUBLE,
    tip_amount               DOUBLE,
    tolls_amount             DOUBLE,
    improvement_surcharge    DOUBLE,
    total_amount             DOUBLE,
    congestion_surcharge     DOUBLE
)
WITH
    STORAGETYPE = row
GO

CREATE BITMAP INDEX PULocationID ON NYTaxi.RowRides(PULocationID)
GO

CREATE BITMAP INDEX passenger_count ON NYTaxi.RowRides(passenger_count)
GO

CREATE INDEX pickup_time ON NYTaxi.RowRides(tpep_pickup_datetime)
GO

CREATE TRIGGER "" BEFORE INSERT
    ON NYTaxi.RowRides
    FOR EACH ROW
LANGUAGE OBJECTSCRIPT
{
 // NOOP to avoid FastINSERT date validation
 quit $$$OK
}
GO

CREATE TABLE NYTaxi.Zones(
    LocationID      INTEGER NOT NULL,
    Zone            VARCHAR(300),
    Borough         VARCHAR(300),
    Shape_Length    DOUBLE,
    Shape_Area      DOUBLE,
    Geometry        VARCHAR(),
    ObjectID        INTEGER,
    CONSTRAINT LocationID PRIMARY KEY(LocationID)
)
GO