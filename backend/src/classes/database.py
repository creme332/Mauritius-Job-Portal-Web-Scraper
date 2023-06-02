#!venv/bin/python3
from __future__ import annotations
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import pandas as pd
from analyser.dictionaryUtils import merge_dicts


class Database:
    """
    Manages the Firestore database
    """

    def __init__(self, service_key: dict, appName: str = ""):
        """
        Initialises firestore client

        Args:
            service_key (dict): Service key of firestore database
        """

        cred = credentials.Certificate(service_key)
        app = None
        if appName == "":
            app = firebase_admin.initialize_app(cred)  # DEFAULT app
        else:
            app = firebase_admin.initialize_app(cred, name=appName)

        # print(app.name)
        self.db = firestore.client(app)

        # save reference to collection for saving scraped jobs
        self.job_collection_ref = self.db.collection(u'jobs_collection')

        # save reference to collection for saving statistics extracted
        # from job collection
        self.stats_collection_ref = self.db.collection(u'statistics')

        # initialise references to documents in stats_collection
        self.db_size_ref = self.stats_collection_ref.document(
            u'database_size')  # stores number of docs in jobs_collection
        self.cloud_data_ref = self.stats_collection_ref.document(u'cloud_data')
        self.db_data_ref = self.stats_collection_ref.document(u'db_data')
        self.lang_data_ref = self.stats_collection_ref.document(u'lang_data')
        self.lib_data_ref = self.stats_collection_ref.document(u'lib_data')
        self.loc_data_ref = self.stats_collection_ref.document(u'loc_data')
        self.os_data_ref = self.stats_collection_ref.document(u'os_data')
        self.salary_data_ref = self.stats_collection_ref.document(
            u'salary_data')
        self.tools_data_ref = self.stats_collection_ref.document(u'tools_data')
        self.web_data_ref = self.stats_collection_ref.document(u'web_data')

        # create documents if missing from database
        if self.create_doc_if_missing(self.db_size_ref):
            self.recalculate_size_counter()
        self.create_doc_if_missing(self.cloud_data_ref)
        self.create_doc_if_missing(self.db_data_ref)
        self.create_doc_if_missing(self.lang_data_ref)
        self.create_doc_if_missing(self.lib_data_ref)
        self.create_doc_if_missing(self.loc_data_ref)
        self.create_doc_if_missing(self.os_data_ref)
        self.create_doc_if_missing(self.salary_data_ref)
        self.create_doc_if_missing(self.tools_data_ref)
        self.create_doc_if_missing(self.web_data_ref)

    def get_dataframe(self) -> pd.DataFrame:
        """
        Fetches the entire database from firestore and returns it as
        a Panda dataframe.

        `WARNING`: Use this function sparingly as it will
        heavily impact the quota usage for number of reads.

        Returns:
            pd.DataFrame: All scraped jobs
        """
        jobs = self.job_collection_ref.stream()
        jobs_dict = list(map(lambda x: x.to_dict(), jobs))
        return pd.DataFrame(jobs_dict)

    def get_recent_urls(self, LIMIT: int = 500) -> list[str]:
        """
        Returns a list of the urls of recently scraped jobs. This function
        can be used to preventing adding duplicates when scraping.

        - Keep 5 < `LIMIT` < 1000 to avoid exceeding read quotas.

        Args:
            LIMIT(int, optional): Maximum number of urls to be
            returned. Defaults to 500.

        Returns:
            list[str]: A list urls
        """
        # get the most recent scraped jobs
        jobs = (self.job_collection_ref

                .order_by("timestamp",
                          direction=firestore.Query.DESCENDING)  # type: ignore
                .limit(LIMIT)
                .stream())

        # convert to a list of dictionaries
        jobs_list = list(map(lambda x: x.to_dict(), jobs))

        # return only the urls
        if len(jobs_list) > 0:
            return pd.DataFrame(jobs_list)['url'].values.tolist()
        return []

    def add_job(self, jobDictionary: dict) -> None:
        """
        Add job to database.

        Args:
            jobDictionary(dictionary): A dictionary with the following keys:
            `job_title`, `date_posted`, `closing_date`, `url`, `location`,
            `employment_type`, `company`, `salary`, `job_details`, `timestamp`
        """
        update_time, job_ref = self.job_collection_ref.add(jobDictionary)
        # print(f'Added document with id {job_ref.id} at: {update_time}')

    def duplicates_exist(self) -> bool:
        """
        Uses `url` as primary key and checks for duplicate jobs in database.
        Result is printed out.

        WARNING: Use this function sparingly as it will
        heavily impact the quota usage for number of reads.

        Returns:
            bool: True if duplicates exist
        """
        # https://stackoverflow.com/a/14657511/17627866
        df = self.get_dataframe()
        ids = df["url"]
        df = df[ids.isin(ids[ids.duplicated()])].sort_values("url")
        if (len(df) > 0):
            print(df)
            return True
        print('No duplicate jobs found.')
        return False

    def get_size(self) -> int:
        """
        Returns the number of jobs in database.

        Returns:
            int: The number of jobs stored in `job_collection`
        """
        return int(self.db_size_ref.get().to_dict()['size'])

    def update_size_counter(self, new_size: int) -> None:
        """
        Updates the value of `size` in the `database_size` document
        in `statistics` collection

        Args:
            new_size(int): Number of documents in jobs_collection
        """
        if new_size >= 0:
            self.db_size_ref.update({'size': new_size})

    def recalculate_size_counter(self) -> None:
        """
        Initialises  the counter which keeps tracks of the
        number of jobs in database to its true value.

        WARNING: Use this function sparingly as it will
        heavily impact the quota usage for number of reads.
        """
        new_size = len(self.get_dataframe())
        self.db_size_ref.update({'size': new_size})

    def sanitize_dict(self, dict: dict) -> dict:
        """
        Dictionary key names containing characters other than
        letters, numbers, and underscores must be sanitized
        before using it.

        https://cloud.google.com/python/docs/reference/firestore/latest/field_path
        """
        new_dict = {}
        for key in dict.keys():
            new_dict[self.db.field_path(key)] = dict[key]
        return new_dict

    def update_stats(self, incrementDict: dict,
                     document_ref) -> None:
        """
        Increments the dictionary of a document in the statistics collection
        by a certain amount.

        Args:
            incrementDict(dict): The dictionary which must be added to
            the currently stored dictionary.
            documentName(dict): Name of document in the `statistics`
            collection containing a dictionary.
        """

        current_doc = document_ref.get()

        if (not current_doc.exists):
            raise Exception(f"{document_ref}"
                            "is missing")

        current_dict = self.sanitize_dict(current_doc.to_dict())

        # combine dictionaries by adding values
        resultDict = merge_dicts(
            current_dict, self.sanitize_dict(incrementDict))

        # if there's no change do nothing
        if (resultDict == current_dict):
            return

        # save changes
        document_ref.update(resultDict)

    def create_doc_if_missing(self, document_ref, initial_val={}) -> bool:
        """
        Checks if a document exists and creates it if not.

        Args:
            document_ref (firestore.documentReference): _description_
            initial_val (dict, optional): Default value stored in document.
            Defaults to {}.
        Returns:
            bool: True if document was missing. False otherwise.
        """
        if (not document_ref.get().exists):
            document_ref.set(initial_val)
            return True
        return False

    def get_doc(self, document_ref) -> dict:
        return document_ref.get().to_dict()

    def get_doc_as_df(self, document_ref, header) -> pd.DataFrame:
        """
        Returns data from a document in `statistics` collection.

        Args:
            document_ref (firestore.document): Reference to document
            header (string): Name of first column. Name of second column is
            frequency.

        Returns:
            pd.DataFrame: Data from document in a table with 2 columns.
        """
        dict = self.get_doc(document_ref)
        df = pd.DataFrame.from_dict(dict, orient='index')
        df = df.reset_index()
        df.columns = [header, 'Frequency']
        return df

    def add_doc(self, collection_ref, doc_id,  doc_data: dict) -> None:
        doc_ref = collection_ref.document(doc_id)
        if (doc_ref.get().exists):
            doc_ref.set(doc_data)

    def export_collection(self, collection_ref):
        """
        Exports a collection. Use this function together with
        `import_collection`

        Args:
            collection_ref (_type_): Reference to firestore collection

        Returns:
            _type_: _description_
        """
        return collection_ref.stream()

    def import_collection(self, collection_ref, collection_stream) -> None:
        """
        Imports a collection to database. Use this function
        together with `export_collection`

        Args:
            collection_ref (_type_): _description_
            collection_stream (_type_): _description_
        """
        for doc in collection_stream:
            self.add_doc(collection_ref, doc.id, doc.to_dict())