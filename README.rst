Python boto3 Document Quick Search
==============================================================================


What is this?
------------------------------------------------------------------------------
I create an `Alfred Workflow <https://www.alfredapp.com/workflows/>`_ framework called `Full Text Search Anything <https://github.com/MacHu-GWU/afwf_fts_anything-project>`_. You can bring your own json data, define how you gonna index it, then use Alfred Workflow to search it.

**This project allows you to quickly search and browse Python boto3 api documents**. It automates the creation of the "your own json data" for boto3 document searching.


How it Work?
------------------------------------------------------------------------------
The `build_data.py <./build_data.py>`_ is a crawler that scrape information from https://boto3.amazonaws.com, and generate a json file like this::

    [
        {
            "title": "S3.get_object",
            "url": "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.get_object",
            "ngram_field": "s3 get object"
        },
        {
            "title": "S3.put_object",
            "url": "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_object",
            "ngram_field": "s3 put object"
        },
        ...
    ]

Just run the following script, it will generate the data file and setting file on Git repo root directory.

.. code-block:: bash

    python3 build_data.py


How to Install?
------------------------------------------------------------------------------
**The automate way**:

    We have a `installation script <./install.py>`_, so just do:

    .. code-block:: bash

        python3 -c "$(curl -fsSL https://raw.githubusercontent.com/MacHu-GWU/alfred-python-boto3-ref/main/install.py)"

**The manual way**:

    You can also download the dataset directly from `Release <https://github.com/MacHu-GWU/alfred-python-boto3-ref/releases>`_. Just Download ``python-boto3-data.zip``, extract it in ``${HOME}/.alfred-fts``. Follow Alfred Workflow Config instruction in https://github.com/MacHu-GWU/afwf_fts_anything-project
