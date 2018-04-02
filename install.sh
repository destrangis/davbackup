py=$( which python3 )
if [[ -z $py ]]
then
    echo "Python3 not in path. Exiting."
    exit 1
fi

ldir=$( dirname $0 )
cd $ldir

$py -m venv .
source bin/activate
pip install -r requirements.txt
