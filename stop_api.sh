DIRNAME=`dirname $0`
cd $DIRNAME
PID=`realpath api.pid`
start-stop-daemon -K -p $PID --remove-pidfile