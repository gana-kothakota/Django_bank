set -o errexit 
set -o nounset 
set -o pipefail 


python manage.py collectstatic --noinput
python manage.py migrate --noinput
exec  python manage.py runserver 0.0.0.0:8000
