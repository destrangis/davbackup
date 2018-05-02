ldir=$( dirname $0 )
cd $ldir

source bin/activate
python3 ./davbackup.py $@
