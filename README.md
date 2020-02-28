# oyara
Simple web API for debits and credits on bank accounts

### Setup server

1. Install [Django](https://docs.djangoproject.com/en/3.0/topics/install/)
2. Install [Django Rest Framework](https://pypi.org/project/djangorestframework/)
3. Run
```
python manage.py runserver
```
4. Visit http://localhost:8000 in your browser

### Setup database

Run the following commands

```
python manage.py makemigrations
python manage.py migrate
```

### Load database with data

Run

```
python manage.py loaddata db_data.txt
```
