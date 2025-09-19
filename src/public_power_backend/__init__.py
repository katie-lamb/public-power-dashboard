"""A template repository for a Python package created by Catalyst Cooperative."""

import importlib.metadata
import logging

# In order for the package modules to be available when you import the package,
# they need to be imported here somehow. Not sure if this is best practice though.
import public_power_backend.cli
import public_power_backend.constants
import public_power_backend.dummy  # noqa: F401
import public_power_backend.etl
import public_power_backend.extract
import public_power_backend.extract.pudl_data
import public_power_backend.transform
import public_power_backend.transform.pudl_data

__author__ = "Catalyst Cooperative"
__contact__ = "pudl@catalyst.coop"
__maintainer__ = "Catalyst Cooperative"
__license__ = "MIT License"
__maintainer_email__ = "pudl@catalyst.coop"
__version__ = importlib.metadata.version("catalystcoop.public_power_backend")
__docformat__ = "restructuredtext en"
__description__ = "A template for Python package repositories."
__long_description__ = """
This should be a paragraph long description of what the package does.
"""
__projecturl__ = "https://github.com/catalyst-cooperative/public_power_backend"
__downloadurl__ = "https://github.com/catalyst-cooperative/public_power_backend"

# Create a root logger for use anywhere within the package.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
