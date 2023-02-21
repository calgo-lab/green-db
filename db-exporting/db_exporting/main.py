import json
import logging
import os
from datetime import date
from pathlib import PurePath
from typing import Iterable, List, Tuple, Union

import pandas as pd
import requests

from core import log
from core.domain import Product, SustainabilityLabel
from database.connection import GreenDB

log.setup_logger(__name__)
logger = logging.getLogger(__name__)

ZENODO_PREFIX = "https://zenodo.org/record"
DEPOSITION_DOI = "https://doi.org/10.5281/zenodo.6078038"
DEPOSITION_BASE_URL = "https://zenodo.org/api/deposit/depositions"
ACCESS_TOKEN = os.environ.get("ZENODO_API_KEY", None)

COLUMNS_COUNT = 20
SUCCESSFUL_STATUS_CODES = {200, 201, 202}

PRODUCTS = "products"
LABELS = "sustainability_labels"

VERSION_INDEX = 2


def extract_deposition_id_and_timestamp(url: str, params: dict) -> Tuple[str, str]:
    """Extracts the Deposition ID and the timestamp from the latest Zenodo version (`url`).

    :param url: The URL to the latest Zenodo version.
    :param params: The params needed to access the deposition via the Zenodo API.
    :return:
        The latest deposition_id and version.
    """
    deposition_id = PurePath(url).name
    r = requests.get(f"{DEPOSITION_BASE_URL}/{deposition_id}", params=params)
    data = r.json()
    version = data["metadata"]["version"]
    return deposition_id, version


def increment_version(version: str) -> str:
    """Increments the patch number of the `version`.

    E.g. version = 1.2.3; returns 1.2.4

    :param version: The deposition version as a string
    :return:
        The patch-incremented `version`.
    """
    try:
        version_split = version.split(".")
        current_version = int(version_split[VERSION_INDEX])
        version_split[VERSION_INDEX] = str(current_version + 1)
        return ".".join(version_split)
    except Exception as e:
        logger.warning(
            f"There's been an issue while incrementing the {version} - {e}. Exiting..."
        )
        raise


def check_request_status(response: requests.Response, step: str) -> None:
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


def prepare_metadata(metadata: dict, version: str) -> Tuple[dict, str]:
    """Prepares the metadata for the publishing request.

    Extracts the metadata from the Zenodo Api (`response_data`) for creating the new deposition;
    Sets the response_data to today's date;
    Replaces the version number with a new incremented version number.

    :param metadata: The metadata from the response object which was obtained by the Zenodo Api,
        for creating the new deposition.
    :param version: The version of the latest deposition.
    :return:
        The new metadata as a dict to be send to Zenodo's '/actions/publish' ,
        containing the updated publication data and version.
    """
    data = {"metadata": metadata}
    data["metadata"]["publication_date"] = str(date.today())
    new_version = increment_version(version)
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
        The new deposition id, the new deposition version, bucket and metadata.
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
    data, new_version = prepare_metadata(r.json()["metadata"], version)

    return new_id, new_version, bucket, data


def export_to_zenodo(
    filenames: List[str], deposition_id: str, version: str, params: dict
) -> None:
    """Export the files [`filenames`] to Zenodo, with updated `deposition_id` and a new `version`.

    :param filenames: A list of local filenames to be uploaded to Zenodo.
    :param deposition_id: The new deposition id to be used for the data upload.
    :param version: The latest version of the deposition (to be later increased).
    :param params: The parameters needed for the Zenodo API.
    """

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


def to_df(objects: Iterable[Union[Product, SustainabilityLabel]]) -> pd.DataFrame:
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
    logger.info("Fetching data from GreenDB")
    db_conn = GreenDB()
    unique_aggregated_urls = db_conn.get_aggregated_unique_products()
    db_products = db_conn.get_products_with_ids(
        unique_aggregated_urls["id"].astype(int)
    )
    db_products = to_df(db_products)

    # Preprocess the data.
    products = process_db_data(unique_aggregated_urls, db_products)

    assert len(products.columns) == COLUMNS_COUNT

    # Store the products files locally.
    products.to_parquet(f"{PRODUCTS}.parquet", index=False)
    products.to_csv(f"{PRODUCTS}.csv", index=False)

    # Get the labels from the db and store the labels files locally.
    labels = to_df(db_conn.get_sustainability_labels())
    labels.to_parquet(f"{LABELS}.parquet", index=False)
    labels.to_csv(f"{LABELS}.csv", index=False)

    logger.info(f"Exporting {products.shape[0]} products and {labels.shape[0]} labels")

    return [
        f"{PRODUCTS}.parquet",
        f"{PRODUCTS}.csv",
        f"{LABELS}.parquet",
        f"{LABELS}.csv",
    ]


def resolve_deposition_url() -> str:
    """Resolves the latest Zenodo URL (containing the Deposition ID) from `DEPOSITION_DOI`.

    Tracks and returns the redirection of the `DEPOSITION_DOI` url
    to the latest Zenodo url of the deposition.

    E.g starts with https://doi.org/10.5281/zenodo.6078038, and will trace the redirection
    to https://zenodo.org/record/7568712 (which is the latest version currently, on 20.02.23)

    :return:
        The latest Zenodo url of the deposition.
    """
    response = requests.head(DEPOSITION_DOI, allow_redirects=True)
    return response.url


def start() -> None:
    """A starting point for the db export.

    Reads the latest deposition_id and version;
    Exports the db data and stores them locally (main::export_db_data);
    Exports the data to Zenodo.
    """
    params = {"access_token": ACCESS_TOKEN}
    # Fetch the deposition_id and version.
    deposition_id, version = extract_deposition_id_and_timestamp(
        resolve_deposition_url(), params
    )

    # Export the db data and get their locally stored data files.
    data_files = export_db_data()
    # Export the data files to zenodo
    export_to_zenodo(data_files, deposition_id, version, params)

    logger.info("Cleanup ... removing cached files locally")
    for file in data_files:
        os.remove(file)
