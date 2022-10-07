# Row vs Column Storage

In InterSystems IRIS®, a relational table, such as the one shown here, is a logical abstraction. It does not reflect the underlying physical storage layout of the data.

![image info](https://github.com/grongierisc/iris-devslam/blob/master/misc/img/table_abstraction.png?raw=true)

## How data can actually be stored

The underlying physical storage layout of the data can be either row or column oriented. In row-oriented storage, the data for each row is stored together. In column-oriented storage, the data for each column is stored together.

### Row storage

In row storage, the data for each row is stored together. This is the default storage layout in InterSystems IRIS.

![image info](https://github.com/grongierisc/iris-devslam/blob/master/misc/img/table_row_storage.png?raw=true)

### Column storage

In column storage, the data for each column is stored together.

![image info](https://github.com/grongierisc/iris-devslam/blob/master/misc/img/table_col_storage.png?raw=true)

## Demo

In this demo, we will show the difference between row storage and column storage.
For that we will create 4 tables with the same data but with different storage layout.

* Demo.BankTransactionRow
  * A Table that store data in row
* Demo.BankTransactionColumn
  * A Table that store data in column
* Demo.BankTransactionIndex
  * A Table that store data in row but with an index in column
* Demo.BankTransactionMix
  * A Table that store data in row and in column

### Let's start

First we will import utils functions that will help us to generate data and to measure the time.

```python
from utilsrowcolumn import * 
```

Then we will create the 4 tables.

Clean up the database

```python
```

### Row storage

## Now let's insert data in the table

It will be done in 2 steps:
* First we will generate data
* Second we will duplicate the data in the table

The first parameter is the number of rows to generate per table.
The second parameter is the number of duplication to generate.

```python
```


```python
```
