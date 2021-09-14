# e-menu
REST API for managing a restaurant menu

# Useful commands for local development

To run the local solution with Docker Compose:
<pre>EMAIL_HOST_USER='your email' EMAIL_HOST_PASSWORD='email (one-time) pass' EMAIL_HOST='smtp.gmail.com(for example)' POSTGRES_PASS='(anything here)' docker-compose up --build</pre>
Then, find the 'app' container id.
<pre>docker ps</pre>
You'll need it to run the following commands.

To run tests and get coverage:
<pre>docker exec -it app_container_id coverage run --source='emenu/' --omit='*/tests.py,*/wsgi.py,*/asgi.py,*/migrations/*' manage.py test
docker exec -it app_container_id coverage report
# or
docker exec -it app_container_id coverage html</pre>

To create a Django superuser:
<pre>docker exec -it app_container_id python3 manage.py createsuperuser </pre>

To insert example test data to the database:
<pre>docker exec -it app_container_id python3 manage.py loaddata testing.json</pre>


