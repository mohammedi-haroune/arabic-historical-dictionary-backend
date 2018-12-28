# arabic-historical-dictionary-backend

You should keep the sql_proxy running !

```
./cloud_sql_proxy -instances=polished-citron-223806:us-central1:tal-sql=tcp:5432 -credential_file=credentials.json
```

Export database credentials before run `python manage.y runserver`
```
export DATABASE_USER=tal                           
export DATABASE_PASSWORD=tal
```