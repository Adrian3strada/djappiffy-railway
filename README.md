# Forestiffy website

Code for site at: http://www.forestiffy.com


## Getting started

Make sure Python 3.5 or higher is installed on your system.
Open this directory in a command prompt, then:

1. Create a development environment.

2. Install the software, and the dev tooling:
   ```
   pip install -r requirements.txt -r requirements-dev.txt
   ```
   __Note:__ If you are using MacOs we recommend install `gdal==3.9.3` using Conda to manage it.

3. Set the environment variables `GDAL_LIBRARY_PATH`, `GEOS_LIBRARY_PATH` and `SPATIALITE_LIBRARY_PATH` to the location which are installed.

4. Propagate the models used in this project for the database schema.
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Include the `django-cities-light` add-on using:
   ```
   python manage.py cities_light
   ```
   __Note:__ This process could take a long time _(20 min aprox)_.

6. Load the __admin__ user configuration.
   ```
   python manage.py loaddata __fixtures/000_users_user.json
   python manage.py loaddata __fixtures/001_profiles_userprofile.json
   python manage.py loaddata __fixtures/002_base_productkind.json
   python manage.py loaddata __fixtures/003_billing_legalentitycategory.json
   python manage.py loaddata __fixtures/004_organizations_organization.json
   python manage.py loaddata __fixtures/005_organizations_organizationuser.json
   python manage.py loaddata __fixtures/006_organizations_organizationowner.json
   python manage.py loaddata __fixtures/007_profiles_organizationprofile.json
   python manage.py loaddata __fixtures/008_packhouse_settings_dev.json
   python manage.py loaddata __fixtures/009_catalogs_dev.json
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Go to http://localhost:8000/dadmin in your browser
   to log in.

8. Access using the __admin__ credentials.


## Linting / pre-deployment

_Building!_


## Documentation links

* To customize the content, design, and features of the site see
  [Wagtail CRX](https://docs.coderedcorp.com/wagtail-crx/).

* For deeper customization of backend code see
  [Wagtail](http://docs.wagtail.io/) and
  [Django](https://docs.djangoproject.com/).

* For HTML template design see [Bootstrap](https://getbootstrap.com/).

---

Made with ♥ using [Wagtail](https://wagtail.io/) +
[CodeRed Extensions](https://www.coderedcorp.com/cms/)
