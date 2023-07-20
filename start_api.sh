DIRNAME=`dirname $0`
cd $DIRNAME
PYTHON_PATH=`poetry env info --executable`
PID=`realpath api.pid`
start-stop-daemon -Sbx $PYTHON_PATH -d ./ -mvp $PID -- ./main.py