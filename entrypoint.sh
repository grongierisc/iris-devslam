#!/bin/bash

set -m

/iris-main "$@" &

/usr/irissys/dev/Cloud/ICM/waitISC.sh

/home/irisowner/.local/bin/jupyter-notebook --no-browser --port=8888 --ip 0.0.0.0 --notebook-dir=/irisdev/app/src/ --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.disable_check_xsrf=True &

redis-server &

fg %1