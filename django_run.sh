CONFIG_FILE=./sup_scripts/rinpy_config.sh
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR! '$CONFIG_FILE' does not exist, create it from the template file 'rinpy_config_template.sh'."
    exit 1
fi
echo 'give the program unlimited (by time) root access (1. sudo visudo  2. add line: Defaults timestamp_timeout=-1)'
sudo echo
. $CONFIG_FILE
RINPY_PATH=$(pwd)
cd /home/restricted_user/
python3 ${RINPY_PATH}/RinPy/manage.py runserver $RINPY_DJ_IP
