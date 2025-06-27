Start at the backend folder.

To run on local this first create python virtual environment: python -m venv venv

Start virtual environment: venv\Scripts\activate

Install the requirements: pip install -r requirements.txt 

Remove the SSL option in the DATABASES setting in settings.py file in the sub backend folder

Setup all the follow environment variable: DJANGO_SECRET_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT

Start making data migration from csv file to PostgreSQL database: 

python manage.py makemigrations 

and then python manage.py migrate 

and finally python manage.py import_scores

After the migration is completed, type: python manage.py runserver to start the backend server
