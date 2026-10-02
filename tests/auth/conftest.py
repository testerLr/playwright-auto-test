"""Auth-domain conftest.

The ``logged_in_page`` fixture lives in the global ``tests/conftest.py``
so that tests in any subdirectory (auth/, inventory/, cart/) can consume
it. This file is kept so pytest still finds a conftest for the auth
package; add auth-specific fixtures here in the future.
"""
