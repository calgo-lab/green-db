import json
import logging
import os
from datetime import date
from typing import List, Tuple, Iterator

import pandas as pd
import requests
from database.connection import GreenDB

from core import log

log.setup_logger(__name__)
logger = logging.getLogger(__name__)

DEPOSITION_BASE_URL = "https://zenodo.org/api/deposit/depositions"
LOCAL_DEPOSITION_VERSION_STORAGE = "/storage/db-exporting/deposition_id_version"
ACCESS_TOKEN = os.environ.get("ZENODO_API_KEY", None)
COLUMNS_COUNT = 20
SUCCESSFUL_STATUS_CODES = [200, 201, 202]

PRODUCTS = "products"
LABELS = "sustainability_labels"

VERSION_INDEX = 2


def increment_version(version: str):
    """Increments the patch number of the `version`.

    E.g. version = 1.2.3; returns 1.2.4

    :param version: The deposition version as a string
    :return:
        The patch-incremented `version`.
    """
    try:
        version = version.split(".")
        current_version = int(version[VERSION_INDEX])
        version[VERSION_INDEX] = str(current_version + 1)
        return ".".join(version)
    except Exception as e:
        logger.warning(
            f"There's been an issue while incrementing the {version} - {e}. Exiting..."
        )
        return None


def check_request_status(response: requests.Response, step: str):
    """Checks if a status of a certain request is invalid and raises an error in that case.

    :param response: The Response from the Zenodo Deposition Api.
    :param step:
        The step in which the response was made = [New Version, File Upload, File Publish..]
    """
    if response.status_code not in SUCCESSFUL_STATUS_CODES:
        logger.warning(response.json())
        error_msg = (
            f"There's been an issue while executing step {step} - "
            f"Request status_code = [{response.status_code}]. Exiting..."
        )
        raise requests.exceptions.RequestException(error_msg)


def prepare_metadata(response_data: dict, version: str) -> Tuple[dict, str]:
    """Prepares the metadata for the publishing request.

    Extracts the metadata from the Zenodo Api (`response_data`) for creating the new deposition;
    Sets the response_data to today's date;
    Replaces the version number with a new incremented version number.


    :param response_data: The data object which was obtained by the Zenodo Api,
        for creating the new deposition.
    :param version: The version of the latest deposition.
    :return:
        The new metadata as a dict to be send to Zenodo's '/actions/publish' ,
        containing the updated publication data and version.
    """
    data = {"metadata": response_data["metadata"]}
    data["metadata"]["publication_date"] = str(date.today())
    new_version = increment_version(version)
    if new_version is None:
        raise ValueError(f"Couldn't parse the version {version}")
    data["metadata"]["version"] = new_version
    return data, new_version


def create_new_version(
    deposition_id: str, version: str, params: dict
) -> Tuple[str, str, str, dict]:
    """Prepares a new version for the deposition with a `deposition_id`.

    :param deposition_id: The id of the latest deposition.
    :param version: The version of the latest deposition.
    :param params: The params needed for the requests, containing 'access_token'.
    :return:
    """
    # Create the new version.
    step = "1. Create new version"
    logger.info(step)
    r = requests.post(
        f"{DEPOSITION_BASE_URL}/{deposition_id}/actions/newversion", params=params
    )
    check_request_status(r, step)

    # Get the new link and the new id for the new version (deposition) of the data.
    new_link = r.json()["links"]["latest_draft"]
    new_id = new_link.split("/")[-1]

    # Request and extract the bucket for data upload for the new version (deposition) of the data.
    step = "2. Get the bucket from the new version"
    logger.info(step)
    r = requests.get(f"{DEPOSITION_BASE_URL}/{new_id}", params=params)
    check_request_status(r, step)
    bucket = r.json()["links"]["bucket"]

    # Extract the metadata for the json file
    data, new_version = prepare_metadata(r.json(), version)

    return new_id, new_version, bucket, data


def export_to_zenodo(filenames: List[str], deposition_id: str, version: str):
    params = {"access_token": ACCESS_TOKEN}
    if ACCESS_TOKEN is None:
        raise ValueError("Access token is required")

    headers = {"Content-Type": "application/json"}

    new_id, new_version, bucket, data = create_new_version(
        deposition_id=deposition_id, version=version, params=params
    )

    # For every filename ...
    for idx, filename in enumerate(filenames):
        with open(filename, "rb") as fp:
            # ...upload it to the bucket..
            step = f"3.{idx + 1} Upload the file [{filename}] to {bucket}"
            logger.info(step)
            r = requests.put("%s/%s" % (bucket, filename), data=fp, params=params)
            # ... check the upload status.
            check_request_status(r, step)

    # Upload the (meta)data.
    step = "4. Upload meta data with the new version and today's date"
    logger.info(step)
    r = requests.put(
        f"{DEPOSITION_BASE_URL}/{new_id}",
        params=params,
        data=json.dumps(data),
        headers=headers,
    )
    check_request_status(r, step)

    # Publish the data and metadata.
    step = "5. Publish "
    logger.info(step)
    url = f"{DEPOSITION_BASE_URL}/{new_id}/actions/publish"
    r = requests.post(url, data=data, params=params)
    check_request_status(r, step)

    return new_id, new_version


def to_df(objects: Iterator) -> pd.DataFrame:
    return pd.DataFrame([obj.__dict__ for obj in objects])


def process_db_data(
    unique_aggregated_urls: pd.DataFrame, products: pd.DataFrame
) -> pd.DataFrame:
    """Further processes the db data.

    Joins the `unique_aggregated_urls` and `products`;
    Applies ::set to the categories;
    Applies a UNISEX gender to the genders columns;

    :param unique_aggregated_urls: The uniquely aggregated urls containing the ids,
        categories and genders from each table row.
    :param products: The exported greendb::green-db products.
    :return:
        The joined data as a dataframe.
    """
    products = products.set_index("url", drop=False)
    unique_aggregated_urls = unique_aggregated_urls.set_index("url")

    joined = unique_aggregated_urls.join(products)
    joined["categories"] = joined["categories"].apply(lambda x: list(set(x)))
    joined["genders"] = joined["genders"].apply(lambda x: list(set(x)))
    joined["genders"] = joined["genders"].apply(
        lambda x: x[0] if len(x) == 1 else "UNISEX"
    )

    joined = joined.drop("gender", axis=1)
    joined = joined.rename(columns={"genders": "gender"})
    joined = joined.drop("category", axis=1)

    return joined.convert_dtypes()


def export_db_data() -> list:
    """Exports (dumps) the db data to local csv files.

    Creates a dump of all unique data rows in the green-db::green-db, a
    nd green-db::sustainability_labels accordingly;
    Stores them as (temporary) parquet and csv files.

    :return:
        The stored file names as a list.
    """
    # Connect to the db, get the unique ids and the products for those ids.
    db_conn = GreenDB()
    unique_aggregated_urls = db_conn.get_aggregated_unique_products()
    products = db_conn.get_products_with_ids(unique_aggregated_urls["id"].astype(int))
    products = to_df(products)

    # Preprocess the data.
    products = process_db_data(unique_aggregated_urls, products)

    assert len(products.columns) == COLUMNS_COUNT

    # Store the products files locally.
    products.to_parquet(f"{PRODUCTS}.parquet", index=False)
    products.to_csv(f"{PRODUCTS}.csv", index=False)

    # Get the labels from the db and store the labels files locally.
    labels = to_df(db_conn.get_sustainability_labels())
    labels.to_parquet(f"{LABELS}.parquet", index=False)
    labels.to_csv(f"{LABELS}.csv", index=False)

    return [
        f"{PRODUCTS}.parquet",
        f"{PRODUCTS}.csv",
        f"{LABELS}.parquet",
        f"{LABELS}.csv",
    ]


def start():
    """A starting point for the db export.

    Reads the latest deposition_id and version;
    Exports the db data and stores them locally (main::export_db_data);
    Exports the data to Zenodo.
    """
    # Read the file with the stored deposition_id and version.
    f = open(LOCAL_DEPOSITION_VERSION_STORAGE, "r")
    deposition_id, version = str(f.read().strip()).split(",")

    # Export the db data and get their locally stored data files.
    data_files = export_db_data()
    # Export the data files to zenodo
    new_deposition_id, new_version = export_to_zenodo(
        data_files, deposition_id, version
    )
    # Finally, write down the new_deposition_id and new version to the same storage file.
    with open(LOCAL_DEPOSITION_VERSION_STORAGE, "w") as f:
        f.write(str(f"{new_deposition_id},{new_version}"))
        logger.info(
            f"Writing latest deposition_id = [{new_deposition_id}] and "
            f"latest version = [{new_version}"
        )

    logger.info("Cleanup ... removing cached files locally")
    for file in data_files:
        os.remove(file)
