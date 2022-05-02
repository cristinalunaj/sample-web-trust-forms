# sample-web-trust-forms
Sample repository to create app to handle forms i Heroku






## INSTALLATION
python3.10


## RUN THE APP (LOCAL):

python app.py



## heroku useful commands:

* (he application is now deployed. Ensure that at least one instance of the app is running:) heroku ps:scale web=1
* heroku open -a sample-web-trust
* heroku logs -a sample-web-trust
* heroku connect:diagnose --verbose -a 
* heroku addons (check plans/DB associated to the app)


## psql

(https://devcenter.heroku.com/articles/connecting-heroku-postgres)
* Configure to psql:    (Configure your user:https://stackoverflow.com/questions/17633422/psql-fatal-database-user-does-not-exist) user286539
* export DATABASE_URL=postgres://$(whoami)
* conn = psycopg2.connect("dbname=suppliers user=cris")


1. CREATE DATABASE suppliers;
2. \c suppliers       (Change to database suppliers)
3. \dt   (list tables on database)
4. CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);
5. SELECT * FROM test;

