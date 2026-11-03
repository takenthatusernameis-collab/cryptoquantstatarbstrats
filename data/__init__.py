"""Real Binance market data loader and cache.

The ``data`` package exposes :mod:`data.loader` and :mod:`data.cache`.  The
``data/cache/`` directory on disk holds pickled series and is *not* a Python
sub-package; it is referenced only as a filesystem path by
:mod:`data.cache`.  Declaring the package explicitly removes the
``data.cache`` module/namespace ambiguity that static type checkers flag
when both ``data/cache.py`` and the ``data/cache/`` directory coexist.
"""
