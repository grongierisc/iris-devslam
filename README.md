# DevSlam 2022 - Iris an multidimensional database

In this git, you will find examples on how IRIS can be an fast an flexible database.

![image info](https://raw.githubusercontent.com/grongierisc/iris-devslam/master/misc/img/Main.jpg)


IRIS can be seen as an multidimensional database what does that mean ?

![image info](https://raw.githubusercontent.com/grongierisc/iris-devslam/master/misc/img/Dimension.jpg)

Here is some dimension, this is not exautif.

In this demo we will be play with few of thoses dimentions.

## Click, Click, GO

To run this demo, you just need to clone this git :

```bash
git clone https://github.com/grongierisc/iris-devslam.git
```

Then run the docker-compose file :

```bash
docker-compose up -d
```

Then you will able to access all the notebook below.

## Dimension **Row store and Column store**

![image](https://user-images.githubusercontent.com/47849411/194313385-fb65c736-dbbc-4ed1-a048-5e3f7646fe29.png)

In this first demo we will learn the diffrance between row storage and column storage.

Then we will generate 1 billion of rows in less than 3 minutes.

Those data will help us to understand the benefit of column storage.

on-prems :

http://127.0.0.1:8888/notebooks/row_column/demo.ipynb

source file :

[link to github](https://github.com/grongierisc/iris-devslam/blob/master/src/python/row_column/demo.ipynb)

## Dimension **In-Memory and Disk**

![image info](https://www.acquire.com.au/wp-content/uploads/2017/03/speed.jpg)

In this second demo we will compare the performance of IRIS vs Redis.

Redis is an in-memory database, IRIS can alse act as an in-memory database with option to persist data on disk.

Will this option make IRIS slower ?

on-prems :

http://127.0.0.1:8888/notebooks/bench_redis_iris/demo.ipynb

source file :

[link to github](https://github.com/grongierisc/iris-devslam/blob/master/src/python/bench_redis_iris/demo.ipynb)


## Dimension **SQL and NoSQL**

![image info](https://media.geeksforgeeks.org/wp-content/cdn-uploads/20191104165821/SQL-Vs-NoSQL1.png)

Just after reaching the speed of light, we will see how IRIS can be used as an SQL database and as an NoSQL database at the same time.

on-prems :

http://127.0.0.1:8888/notebooks/multi_model/demo.ipynb

source file :

[link to github](https://github.com/grongierisc/iris-devslam/blob/master/src/python/multi_model/demo.ipynb)

## **The python framework**

This is the IRIS Framework.

![FrameworkFull](https://raw.githubusercontent.com/thewophile-beep/formation-template/master/misc/img/FrameworkFull.png)

The components inside of IRIS represent a production. Inbound adapters and outbound adapters enable us to use different kind of format as input and output for our database. <br>The composite applications will give us access to the production through external applications like REST services.

The arrows between them all of this components are **messages**. They can be requests or responses.

And finally we will talk about the python framework.

This framework help you to organize you python code in a way that is easy to understand and easy to maintain.

