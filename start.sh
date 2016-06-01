#!/usr/bin/env bash
cd $( dirname $0 )
if [[ ! -d ./v ]];then
    rm -f ./v
    mkdir ./v
    virtualenv ./v
fi
. v/bin/activate
[[ -f ./requirements.txt ]] && pip install -r ./requirements.txt
[[ -f ../secrets.sh ]] && . ../secrets.sh
python manage.py runserver &
