py=$( which python3 )
if [[ -z $py ]]
then
    echo "Python3 not in path. Exiting."
    exit 1
fi

ldir=$( dirname $0 )
cd $ldir

echo "Creating virtual environment."
$py -m venv .
echo "Activating virtual environment."
source bin/activate
echo "Installing dependencies."
pip install -r requirements.txt
echo "Done."
