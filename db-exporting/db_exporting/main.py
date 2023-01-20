from datetime import date

import json
import os
import pandas as pd

from db_exporting.db_connection import DBConnection
import requests

DEPOSITION_ID = os.environ.get("DEPOSITION_ID", None)
# todo add it as a secret
ACCESS_TOKEN = "dRC51Ri9Td7aQSjtmgLBYqQVaZ8ymBQuZJMkb72billaWhgy3Z8Py2K1Rrtj"

COLUMNS_COUNT = 20

r = {'conceptdoi': '10.5072/zenodo.1143578', 'conceptrecid': '1143578', 'created': '2023-01-20T13:08:47.643567+00:00',
     'doi': '10.5072/zenodo.1149632', 'doi_url': 'https://doi.org/10.5072/zenodo.1149632', 'files': [{'checksum':
                                                                                                          'a92ad26c3c69b538c3f7b0f478f9a993',
                                                                                                      'filename': 'products.csv',
                                                                                                      'filesize': 1723623,
                                                                                                      'id': '7c43c945-2cae-4f91-87db-7a3b8a58903b',
                                                                                                      'links': {
                                                                                                          'download':
                                                                                                              'https://sandbox.zenodo.org/api/files/7e00e6a4-63c3-4ced-aeed-b611713e49b7/products.csv',
                                                                                                          'self': 'https://sandbox.zenodo.org/api/deposit/depositions/1149632/files/7c43c945-2cae-4f91-87db-7a3b8a58903b'}},
                                                                                                     {
                                                                                                         'checksum': '675eb3dfdd7628d416ecffc3f64932cc',
                                                                                                         'filename': 'products.parquet',
                                                                                                         'filesize': 524629,
                                                                                                         'id': 'e52f37ad-a044-4be7-a266-75593ca361ad',
                                                                                                         'links': {
                                                                                                             'download':
                                                                                                                 'https://sandbox.zenodo.org/api/files/7e00e6a4-63c3-4ced-aeed-b611713e49b7/products.parquet',
                                                                                                             'self': 'https://sandbox.zenodo.org/api/deposit/depositions/1149632/files/e52f37ad-a044-4be7-a266-75593ca361ad'}},
                                                                                                     {
                                                                                                         'checksum': '95de8d2b0856d45e30008859a93f08f4',
                                                                                                         'filename': 'sustainability_labels.csv',
                                                                                                         'filesize': 154758,
                                                                                                         'id': 'e0c03683-e14e-408b-ab14-c1141823f853',
                                                                                                         'links': {
                                                                                                             'download':
                                                                                                                 'https://sandbox.zenodo.org/api/files/7e00e6a4-63c3-4ced-aeed-b611713e49b7/sustainability_labels.csv',
                                                                                                             'self': 'https://sandbox.zenodo.org/api/deposit/depositions/1149632/files/e0c03683-e14e-408b-ab14-c1141823f853'}}],
     'id': 1149632, 'links': {'badge': 'https://sandbox.zenodo.org/badge/doi/10.5072/zenodo.1149632.svg',
                              'bucket': 'https://sandbox.zenodo.org/api/files/7e00e6a4-63c3-4ced-aeed-b611713e49b7',
                              'conceptbadge':
                                  'https://sandbox.zenodo.org/badge/doi/10.5072/zenodo.1143578.svg', 'conceptdoi':
                                  'https://doi.org/10.5072/zenodo.1143578',
                              'doi': 'https://doi.org/10.5072/zenodo.1149632', 'latest':
                                  'https://sandbox.zenodo.org/api/records/1149632', 'latest_draft':
                                  'https://sandbox.zenodo.org/api/deposit/depositions/1149643', 'latest_draft_html':
                                  'https://sandbox.zenodo.org/deposit/1149643',
                              'latest_html': 'https://sandbox.zenodo.org/record/1149632',
                              'record': 'https://sandbox.zenodo.org/api/records/1149632', 'record_html':
                                  'https://sandbox.zenodo.org/record/1149632'},
     'metadata': {'access_conditions': '<p>People with access key</p>',
                  'access_right': 'restricted', 'communities': [{'identifier': 'zenodo'}], 'creators': [{'name': 'IT'}],
                  'description': '<p>Some test data</p>', 'doi': '10.5072/zenodo.1149632', 'prereserve_doi': {'doi':
                                                                                                                  '10.5072/zenodo.1149632',
                                                                                                              'recid': 1149632},
                  'publication_date': '2023-01-04', 'title': 'green', 'upload_type':
                      'dataset', 'version': '0.3.0'}, 'modified': '2023-01-20T13:08:52.793136+00:00', 'owner': 136315,
     'record_id':
         1149632, 'state': 'done', 'submitted': True, 'title': 'green'}


#
# publication_date = set to today's date
# publication_date = date(r.json['modified']) -> From HERE 1

def increment_ver(version):
    version = version.split('.')
    version[2] = str(int(version[2]) + 1)
    return '.'.join(version)


def exporter():
    print(DEPOSITION_ID)
    SANDBOX_DEP_ID = DEPOSITION_ID if DEPOSITION_ID else 1149632
    print(SANDBOX_DEP_ID)

    params = {'access_token': ACCESS_TOKEN}

    filenames = ["products.csv", "products.parquet", "sustainability_labels.csv", "sustainability_labels.parquet"]
    print("HERE 1")
    headers = {"Content-Type": "application/json"}
    # base_url = f"https://sandbox.zenodo.org/api/deposit/depositions"
    # r_old = requests.get(f'{base_url}/{SANDBOX_DEP_ID}',
    #                  params=params)
    # print(r_old.json())
    # print(r_old.status_code)

    print("1. Create new version")
    base_url = f"https://sandbox.zenodo.org/api/deposit/depositions"
    r = requests.post(f'{base_url}/{SANDBOX_DEP_ID}/actions/newversion',
                      params=params)
    new_version_r = r.json()
    print(r.json())
    print(r.status_code)

    new_link = r.json()["links"]["latest_draft"]
    new_id = new_link.split("/")[-1]

    print("2. Get the bucket from the new version?")
    r = requests.get(f'{base_url}/{new_id}',
                     params=params)

    bucket = r.json()["links"]["bucket"]
    data = {"metadata": r.json()["metadata"]}
    #todo ivana parse this
    # publication_date = date(new_version_r["modified"])
    publication_date = "2023-01-20"
    data["metadata"]["publication_date"] = publication_date
    data["metadata"]["version"] = increment_ver(data["metadata"]["version"])
    # publication_date = set to today's date
    # parse date
    print(f"NEW ID = {new_id}")
    if new_id:
        os.environ["DEPOSITION_ID"] = new_id

    for filename in filenames:
        # todo update pah accordingly
        path = filename
        with open(path, "rb") as fp:
            print(f"3. Upload the files to {bucket}")
            r = requests.put("%s/%s" % (bucket, filename), data=fp, params=params)
            print(r.json())
            print(r.status_code)

    print(f"4. Upload meta data with the new version and today's date")
    r = requests.put(f'{base_url}/{new_id}',
                     params=params, data=json.dumps(data),
                     headers=headers)
    print(r.json())
    print(r.status_code)

    print("4. Publish ")
    url = f'{base_url}/{new_id}/actions/publish'
    r = requests.post(url, data=data, params=params)
    print(r.json())
    print(r.status_code)


def to_df(objects):
    return pd.DataFrame([product.__dict__ for product in objects])


def aggregate_data():
    db_conn = DBConnection()
    unique_aggregated_urls = db_conn.get_aggregated_unique_products()
    products = db_conn.get_products_with_ids(unique_aggregated_urls["id"].astype(int))
    products = to_df(products)
    joined = unique_aggregated_urls.join(products)

    joined["categories"] = joined["categories"].apply(lambda x: list(set(x)))
    joined["genders"] = joined["genders"].apply(lambda x: list(set(x)))
    joined["genders"] = joined["genders"].apply(lambda x: x[0] if len(x) == 1 else "UNISEX")
    joined.drop("gender", axis=1)
    joined = joined.rename(columns={"genders": "gender"})
    joined = joined.drop("category", axis=1)
    joined = joined.convert_dtypes()

    assert joined.shape[1] == COLUMNS_COUNT

    joined.to_parquet("products.parquet", index=False)
    joined.to_csv("products.csv", index=False)

    labels = to_df(db_conn.get_sustainability_labels())
    labels.to_parquet("labels.parquet", index=False)
    labels.to_csv("labels.csv", index=False)


def shuffle_and_store():
    pr = pd.read_csv("products.csv")
    prq = pd.read_parquet("products.parquet")
    sl = pd.read_csv("sustainability_labels.csv")
    slq = pd.read_parquet("sustainability_labels.parquet")

    pr.sample(frac=1)[:-1].to_csv("products.csv", index=False)
    prq.sample(frac=1)[:-1].to_parquet("products.parquet", index=False)
    sl.sample(frac=1)[:-1].to_csv("sustainability_labels.csv", index=False)
    slq.sample(frac=1)[:-1].to_parquet("sustainability_labels.parquet", index=False)


if __name__ == '__main__':
    # aggregate_data()
    shuffle_and_store()
    # DEPOSITION_ID = os.environ.get("DEPOSITION_ID", None)
    exporter()
