[![Test Status](https://github.com/justinbrick/capstone-project-shipping-api/actions/workflows/python-app.yml/badge.svg)](https://github.com/justinbrick/capstone-project-shipping-api/actions/workflows/python-app.yml)

## Dependencies
Project is using Python 3.11, make sure you have this version installed.

Install dependencies using the following line:
```
pip3 install -r requirements.txt
```

## Environment Variables
There are some environment variables required to access certain APIs. Otherwise, they will be mocked.
It is highly recommended that you add these to a .env file or launch script, so that they do not get added to your working tree.
### Hosting
When you are ready to put the application into production, you must specify the `HOST_NAME` and the `HOST_PORT`.
This should help with reverse proxies and port collisions.
These are optional and by default they are set to `127.0.0.1` and `8000`, respectively.
### Geocoding
Geocoding uses Google Maps API. You can specify the API key using `MAPS_API_KEY`.
If you do not specify a key, `Photon` will be used, and will likely be throttled. 
If you get geocoding errors, please make sure that you have specified a Google Maps API key.
### Auth
There are some fields that are required for authentication and authorization.
- CLIENT_ID: The Client ID of the __API__ application.
- CLIENT_SECRET: The client secret of your __API__ application.
- TENANT_ID: The Tenant ID of your Azure AD B2C Tenant.
- TENANT_SHORT_NAME: The shortname of your Azure AD B2C tenant ({shortname}.onmicrosoft.com)
- USER_FLOW: The name of the Azure AD B2C authorization flow. This WILL be used for token endpoints, too.