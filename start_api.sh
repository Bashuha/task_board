DIRNAME=`dirname $0`
cd $DIRNAME
source venv/bin/activate
PYTHON_PATH=`which python`
PID=`realpath api.pid`
start-stop-daemon -S -b -x $PYTHON_PATH -d ./ -m -v -p $PID -- ./main.py