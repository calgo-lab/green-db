import json
from logging import getLogger
from typing import Union, Iterator, List

from flask import Flask, Response, request
from waitress import serve
import numpy as np
import pandas as pd
from autogluon.multimodal import MultiModalPredictor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
from core.constants import PRODUCT_CLASSIFICATION_MODEL
from core.domain import ProductClassification

from database.connection import GreenDB

logger = getLogger(__name__)

app = Flask(__name__)

model_classes = ['AUDIO HEADSETS', 'BLAZER', 'BLOUSE', 'CLOTHES WASHERS',
                 'COOKER HOODS', 'DENIM_TROUSERS', 'DISHWASHERS', 'DRESSES',
                 'FOOTWEAR', 'FREEZERS', 'JACKETS/CARDIGANS/WAISTCOATS',
                 'OVENS', 'OVERALLS/BODYSUITS', 'PERSONAL CARRIERS',
                 'PERSONAL COMPUTERS - PORTABLE', 'PRINTERS',
                 'RANGE COOKERS/STOVES', 'REFRIGERATORS', 'RUCKSACK',
                 'SHIRTS/POLO SHIRTS/T-SHIRTS', 'SKIRTS', 'SLEEPWEAR',
                 'SLEEVELESS_SHIRT', 'SPIN/TUMBLE DRYERS', 'SWEATERS/PULLOVERS',
                 'SWIMWEAR', 'TABLET PC', 'TRACKSUIT', 'TROUSERS/SHORTS', 'UNDERWEAR']

gpc_to_greendb = {'AUDIO HEADSETS': 'HEADPHONES',
                  'BLAZER': 'JACKET',
                  'BLOUSE': 'BLOUSE',
                  'CLOTHES WASHERS': 'WASHER',
                  'COOKER HOODS': 'COOKER_HOOD',
                  'DENIM_TROUSERS': 'JEANS',
                  'DISHWASHERS': 'DISHWASHER',
                  'DRESSES': 'DRESS',
                  'FOOTWEAR': 'SHOES',
                  'FREEZERS': 'FREEZER',
                  'JACKETS/CARDIGANS/WAISTCOATS': 'JACKET',
                  'OVENS': 'OVEN',
                  'OVERALLS/BODYSUITS': 'OVERALL',
                  'PERSONAL CARRIERS': 'BAG',
                  'PERSONAL COMPUTERS - PORTABLE': 'LAPTOP',
                  'PRINTERS': 'PRINTER',
                  'RANGE COOKERS/STOVES': 'STOVE',
                  'REFRIGERATORS': 'FRIDGE',
                  'RUCKSACK': 'BACKPACK',
                  'SHIRTS/POLO SHIRTS/T-SHIRTS': 'SHIRT',
                  'SKIRTS': 'SKIRT',
                  'SLEEPWEAR': 'NIGHTWEAR',
                  'SLEEVELESS_SHIRT': 'TOP',
                  'SPIN/TUMBLE DRYERS': 'DRYER',
                  'SWEATERS/PULLOVERS': 'SWEATER',
                  'SWIMWEAR': 'SWIMWEAR',
                  'TABLET PC': 'TABLET',
                  'TRACKSUIT': 'TRACKSUIT',
                  'TROUSERS/SHORTS': 'PANTS',
                  'UNDERWEAR': 'UNDERWEAR'}

combine_classes = {
    'JACKETS/CARDIGANS/WAISTCOATS': ['BLAZER', 'JACKETS/CARDIGANS/WAISTCOATS']
}

le = LabelEncoder()
le.fit(model_classes)

features = ["name", "description"]

MODEL_DIR = f"/usr/src/app/data/models/{PRODUCT_CLASSIFICATION_MODEL}"
db_connection = GreenDB()
model = MultiModalPredictor.load(MODEL_DIR)
model.set_num_gpus(0)

def predict_proba(df):
    if not set(features).issubset(set(df.columns)):
        logger.warning(
            f"The dataframe is missing features."
            f"Returning 'None'."
        )
        return None

    logger.info(f"Predicting for {len(df)} products ...")
    pred_probs = model.predict_proba(df)
    logger.info(f"Finished prediction.")
    return pred_probs


def create_ProductClassification(pred_probs) -> List[ProductClassification]:
    pred_probs = convert_classes(pred_probs)
    pred_probs.columns = le.inverse_transform(pred_probs.columns)
    pred_probs.columns = [gpc_to_greendb.get(col) for col in pred_probs.columns]

    predicted_category = [pred_probs.columns[np.argmax(p)] for p in pred_probs.values]
    confidence = [np.max(p) for p in pred_probs.values]

    result = pd.DataFrame({
        "id": pred_probs.index,
        "ml_model_name": PRODUCT_CLASSIFICATION_MODEL,
        "timestamp": datetime.now(),
        "predicted_category": predicted_category,
        "confidence": confidence,
        "all_predicted_probabilities": pred_probs.to_dict(orient='records')
    })

    return result


def convert_classes(pred_probs):
    # combine all column values that have the same greendb category e.g. BLAZER and JACKET/CARDIGANS/WAISTCOATS

    for k, v in combine_classes.items():
        cols_to_combine = le.transform(v)
        max_of_cols = pred_probs.loc[:, cols_to_combine].max(axis=1)
        pred_probs[le.transform([k])[0]] = max_of_cols

        drop_cols = [c for c in v if c != k]
        pred_probs = pred_probs.drop(columns=le.transform(drop_cols))

    return pred_probs


def to_df(objects: Union[list, Iterator]) -> pd.DataFrame:
    """Converts a list or iterator to a df.
    :param objects: A list of objects to be converted to a df.
    :return:
        A dataframe from the `objects`.
    """
    return pd.DataFrame([obj.__dict__ for obj in objects])


def get_latest_products():
    # Get the products from the db
    logger.info(f"Loading latest products from database ...")
    products = db_connection.get_latest_products(convert_orm=False)
    logger.info(f"Loaded {len(products)} latest products from database.")
    products = to_df(products)
    products = products.set_index("id")[features]
    return products


@app.route("/predict_latest")
def certificates_persistence_handler() -> Response:
    """Calls the persist_certificates() in order to precompute and persist the certificates.
    :return:
        A flask Response containing the precomputed certificates.
    """
    df = get_latest_products()

    # TODO: predict only when results are not stored in db
    pred_probs = predict_proba(df)
    result = create_ProductClassification(pred_probs)

    # TODO: write results to db
    db_connection.write_dataframe(result)

    return Response(result.to_json(orient="records"), mimetype="application/json")


@app.route("/", methods=['POST'])
def product_classifier_handler() -> Response:
    """Reads the JSON data from the POST request, which is expected to include product data,
    which is used for inference.

    :return:
        A flask Response containing the predictions.
    """
    request_data = request.get_json()
    df = pd.read_json(request_data)
    pred_probs = predict_proba(df)

    result = create_ProductClassification(pred_probs)
    return Response(result.to_json(orient="records"), mimetype="application/json")


# TODO: add label qualities via cleanlab as well (needs mapping from GreenDB to GPC)


@app.route("/test", methods=['GET'])
def test() -> Response:
    return Response("test")


def create_app():
    serve(app, host="0.0.0.0", port=8282)
    return app
