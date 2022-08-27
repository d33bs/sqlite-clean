.. sqlite-clean documentation master file, created by
   sphinx-quickstart on Sat Aug  6 13:07:13 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SQLite-Clean Documentation
==========================

A SQLite data validation and cleanup tool.

SQLite is an incredibly flexible tool that has great utility in many circumstances.
This flexibility sometimes comes at the cost of later data performance or surprise challenges which can sometimes otherwise be avoided or fixed with checks.
`sqlite-clean` is intended to be used for these checks and enable cleanup steps where possible.

Database changes from this tool are intended to be the choice and responsibility of the user. 
To this effect, `sqlite-clean` provides both "linting" (detection and alerts of possible issues) and "fixes" (actual changes to the database) as separate utilities within the same tool.
By default, "linting" actions are taken unless otherwise specifying flags associated with "fixes".

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   commands
   develop
   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
