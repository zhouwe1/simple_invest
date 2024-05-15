cd /var/www/financing/
git pull
source /var/venv/financing/bin/activate
export FLASK_APP=run.py
#pip install -r requirements.txt
flask db upgrade
exec gunicorn -w 1 --threads=2 -b 127.0.0.1:8001 webapp:flask_app &