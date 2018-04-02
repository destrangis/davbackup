ldir=$( dirname $0 )
cd $ldir
if [ -f nobackup ]
then
    echo "File nobackup present. Not running."
    exit 1
fi
source bin/activate
python ./davbackup.py $@
