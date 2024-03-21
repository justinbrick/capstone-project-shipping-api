[![Test Status](https://github.com/justinbrick/capstone-project-shipping-api/actions/workflows/python-app.yml/badge.svg)](https://github.com/justinbrick/capstone-project-shipping-api/actions/workflows/python-app.yml)

## Dependencies
Project is using Python 3.11, make sure you have this version installed.

Install dependencies using the following line:
```
pip3 install -r requirements.txt
```

## Environment Variables
There are some environment variables required to access certain APIs. Otherwise, they will be mocked.
### Geocoding
Geocoding uses Google Maps API. You can specify the API key using `MAPS_API_KEY`.
