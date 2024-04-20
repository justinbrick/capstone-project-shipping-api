"""
Module for Point of Sale API
"""


import httpx


async def __authorize(request: httpx.Request):
    request.headers['Authorization'] = 'Bearer Token'

client = httpx.AsyncClient(
    base_url='http://localhost:8000', event_hooks={'request': [__authorize]})
