"""Inventory-domain conftest.

The ``inventory`` fixture previously defined here was promoted to the
global ``tests/conftest.py`` in task-11 so cart tests (which are NOT
descendants of this directory) could also consume it. Pytest only
propagates conftest.py fixtures to subdirectories, not siblings, so
defining it here left ``tests/cart/test_cart.py`` unable to resolve
``inventory``. The fixture now lives in ``tests/conftest.py`` and is
visible to every test in ``tests/`` and below. See task-10 report for
the analogous ``logged_in_page`` move.
"""