"""
**File:** ``__init__.py``
**Region:** ``ds-provider-ticketco-py-lib``

Description
-----------
A Python package from the ds-provider-ticketco-py-lib library.

Example
-------
.. code-block:: python

    from ds_provider_ticketco_py_lib import __version__

    print(f"Package version: {__version__}")
"""

from importlib.metadata import version

__version__ = version("ds-provider-ticketco-py-lib")
__all__ = ["__version__"]
