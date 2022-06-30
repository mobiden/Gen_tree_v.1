heroku buildpacks:add --index 1 heroku-community/apt
python manage.py collectstatic --noinput;
release: python manage.py migrate
web: gunicorn Gen_tree.wsgi --log-file -
