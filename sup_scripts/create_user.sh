sudo useradd -m restricted_user
sudo chmod 777 /home/restricted_user
cd ./RinPy/default_user_files
cp -R * /home/restricted_user
