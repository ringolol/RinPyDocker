sudo chmod +x ./sup_scripts/*
echo CREATING USER...
./sup_scripts/create_user.sh
echo LOADING PACKAGES...
./sup_scripts/load_packages.sh
echo 'FINISH!'
echo You can now run django server using './django_run.sh'
