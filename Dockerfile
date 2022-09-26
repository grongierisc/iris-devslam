ARG IMAGE=intersystemsdc/iris-community:latest
FROM $IMAGE

# use the root user to install packages
USER root   

# create a directory for the application     
WORKDIR /irisdev/app
RUN chown ${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} /irisdev/app
USER ${ISC_PACKAGE_MGRUSER}

# Copy the source code
COPY . .
COPY iris.script /tmp/iris.script

# install required packages
RUN pip3 install -r requirements.txt

# environment variables for embedded python
ENV IRISUSERNAME "SuperUser"
ENV IRISPASSWORD "SYS"
ENV IRISNAMESPACE "IRISAPP"

# create the namespace and install the application
RUN iris start IRIS \
	&& iris session IRIS < /tmp/iris.script \
    && /usr/irissys/bin/irispython src/python/register.py \
    && iris stop IRIS quietly



