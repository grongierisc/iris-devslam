ARG IMAGE=intersystemsdc/iris-community:preview
FROM $IMAGE

# use the root user to install packages
USER root   

# update the package list and install the required packages
RUN apt-get update && apt-get install -y \
	git \
	nano \
    redis-server \
	sudo && \
	/bin/echo -e ${ISC_PACKAGE_MGRUSER}\\tALL=\(ALL\)\\tNOPASSWD: ALL >> /etc/sudoers && \
	sudo -u ${ISC_PACKAGE_MGRUSER} sudo echo enabled passwordless sudo-ing for ${ISC_PACKAGE_MGRUSER}

# create a directory for the application     
WORKDIR /irisdev/app
RUN chown ${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} /irisdev/app
RUN mkdir -p /opt/irisapp/data
RUN chown ${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} /opt/irisapp/data
USER ${ISC_PACKAGE_MGRUSER}

# Copy the source code
COPY . .
COPY bashrc /home/irisowner/.bashrc
COPY iris.script /tmp/iris.script

# install required packages
RUN pip3 install -r requirements.txt

# environment variables for embedded python
ENV IRISUSERNAME "SuperUser"
ENV IRISPASSWORD "SYS"
ENV IRISNAMESPACE "IRISAPP"

# Install embedded python kernel
RUN mkdir /home/irisowner/.local/share/jupyter/kernels/irispython
COPY misc/kernels/irispython/* /home/irisowner/.local/share/jupyter/kernels/irispython/

# create the namespace and install the application
RUN iris start IRIS \
	&& iris session IRIS < /tmp/iris.script \
    && /usr/irissys/bin/irispython src/python/register.py \
    && iris stop IRIS quietly

ENTRYPOINT [ "/tini", "--", "/irisdev/app/entrypoint.sh" ]

