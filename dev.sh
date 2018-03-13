# $ source dev.sh
o_path=$PWD
f_path=`dirname $0`
cd $f_path
f_path=$PWD

export FRUMULTEST=0 # enable traceback for development purpose
source ./frumurvenv/bin/activate
alias frumul="$f_path/frumul.py"
alias indexer="$f_path/indexer.py"
cd $o_path
