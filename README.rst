Public Power Dashboard
======================

.. readme-intro

.. image:: https://github.com/catalyst-cooperative/cheshire/workflows/tox-pytest/badge.svg
   :target: https://github.com/catalyst-cooperative/cheshire/actions?query=workflow%3Atox-pytest
   :alt: Tox-PyTest Status

.. image:: https://img.shields.io/codecov/c/github/catalyst-cooperative/cheshire?style=flat&logo=codecov
   :target: https://codecov.io/gh/catalyst-cooperative/cheshire
   :alt: Codecov Test Coverage

.. image:: https://img.shields.io/readthedocs/catalystcoop-cheshire?style=flat&logo=readthedocs
   :target: https://catalystcoop-cheshire.readthedocs.io/en/latest/
   :alt: Read the Docs Build Status

.. image:: https://img.shields.io/pypi/v/catalystcoop.cheshire?style=flat&logo=python
   :target: https://pypi.org/project/catalystcoop.cheshire/
   :alt: PyPI Latest Version

.. image:: https://img.shields.io/conda/vn/conda-forge/catalystcoop.cheshire?style=flat&logo=condaforge
   :target: https://anaconda.org/conda-forge/catalystcoop.cheshire
   :alt: conda-forge Version

.. image:: https://img.shields.io/pypi/pyversions/catalystcoop.cheshire?style=flat&logo=python
   :target: https://pypi.org/project/catalystcoop.cheshire/
   :alt: Supported Python Versions

This repository creates the tables used as the backend for Public Grids's public power
dashboard. Only an initial phase of work was conducted, and there are improvements
still left to be made.

This repo combines data from various sources, including the Public Utility Data
Liberation project (PUDL), affordablity data from PSE Healthy Energy, financial
data from Yahoo Finance, and other sources. The tables are built from a "backbone"
of data on IOUs from EIA Form 860 (via PUDL). The IOUs in this backbone have
been manually filtered by Public Grids and at this point excludes some IOUs.
The EIA utility ID in this IOU backbone serves as the index onto which all other
datasets are merged on.



Create the conda environment
----------------------------

We use ``conda`` to manage packages. Make sure you have [conda installed](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
Once conda is installed, run:

.. code:: python

   conda env create --name pub-power-dev --file environment.yml

Then activate the environment:

.. code:: python

   conda activate dbcp-dev

To materialize the data
-----------------------

To materialize the tables, first create the IOU backbone by running:

.. code:: python

  python -m public_power_dashboard.etl

This creates intermediate Parquet files in the ``data.output.data_warehouse``
directory and an IOU backbone Parquet file in ``data.output.data_mart``.

This IOU backbone table is used to create the remaining tables: regulatory
conditions, utility conditions, utility-genic harms, and ownership conditions.
As this was an initial phase of work, the creation of these tables isn't
fully integrated into the ETL. Instead, these tables are created in Jupyter
notebooks in the ``notebooks`` directory. Running the notebook for each of these
tables creates a Parquet file for the table in the ``data.output.data_mart``
directory. There are some several manual overrides made to the ownership data.
These manual overrides can be found in the ``constants.py`` module as well as
the manual overrides CSVs in the data inputs directory.

One-off data from various other sources, like PSE Healthy Energy, are stored
as CSVs in the data inputs directory.
