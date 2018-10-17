from flask_restplus import Api, Resource
from .site import endpoint as website
from .api import endpoint as api_handler

"""
Module responsible for collecting all the namespaces into the same api
"""

api = Api(
    title='Distributed Computation - Project 4',
    version='1.0',
    description='API structure',
)

api.add_namespace(website)
api.add_namespace(api_handler)

