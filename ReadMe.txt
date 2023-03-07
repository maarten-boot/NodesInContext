# install python3.11
# install postgres 13

(
    cd ..
    python3 -m venv ./NodesInContext
    python3 -m venv --upgrade NodesInContext
)

source $HOME/DEV/Django/NodesInContext/bin/activate
# sudo service gunicorn002 restart
# ./manage.py spectacular --color --file schema.yml
# ./manage.py generateschema --file openapi-schema.yml

pip install --upgrade pip

pip install psycopg2-binary
pip install python-dotenv
pip install "python-dotenv[cli]"
pip install python-ldap
pip install gunicorn
pip install python-environ

pip install Django
pip install Django --upgrade
pip install Django-ldap
pip install django_auth_ldap
pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support
pip install drf-spectacular

# sudo service gunicorn002 restart

# Postgres
# sudo su - postgres
# psql
CREATE USER nicdb WITH PASSWORD '----------';
CREATE DATABASE nic OWNER nicdb;
ALTER ROLE inventorydb SET client_encoding TO 'utf8';
ALTER ROLE inventorydb SET default_transaction_isolation TO 'read committed';
ALTER ROLE inventorydb SET timezone TO 'UTC';

# cd ./DEV/Django/NodesInContext
# django-admin createproject pNic
# cd ./pNic

sudo systemctl daemon-reload
sudo systemctl restart gunicorn002.service

./manage.py migrate
./manage.py createsuperuser
