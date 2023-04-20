import json
from logging import getLogger
from typing import Union, Iterator, List

from flask import Flask, Response, request
from waitress import serve
import numpy as np
import pandas as pd
from autogluon.multimodal import MultiModalPredictor
from sklearn.preprocessing import LabelEncoder
from core.constants import PRODUCT_CLASSIFICATION_MODEL, PRODUCT_CLASSIFICATION_MODEL_FEATURES

from database.connection import GreenDB

logger = getLogger(__name__)

app = Flask(__name__)

model_classes = ['BACKPACK', 'BAG', 'BLOUSE', 'COOKER_HOOD', 'DISHWASHER', 'DRESS',
                 'DRYER', 'FREEZER', 'FRIDGE', 'HEADPHONES', 'HEADSET', 'JACKET',
                 'JEANS', 'LAPTOP', 'LINEN', 'NIGHTWEAR', 'OVEN', 'OVERALL',
                 'PANTS', 'PRINTER', 'SHIRT', 'SHOES', 'SHORTS', 'SKIRT',
                 'SMARTPHONE', 'SMARTWATCH', 'SNEAKERS', 'SOCKS', 'STOVE', 'SUIT',
                 'SWEATER', 'SWIMWEAR', 'TABLET', 'TOP', 'TOWEL', 'TRACKSUIT',
                 'TSHIRT', 'TV', 'UNDERWEAR', 'WASHER']

le = LabelEncoder()
le.fit(model_classes)

MODEL_DIR = f"/usr/src/app/data/models/{PRODUCT_CLASSIFICATION_MODEL}"
db_connection = GreenDB()
model = MultiModalPredictor.load(MODEL_DIR)
model.set_num_gpus(0)


def predict_proba(df):
    logger.info(f"Predicting for {len(df)} products ...")
    pred_probs = model.predict_proba(df)
    logger.info(f"Finished prediction.")
    return pred_probs


def create_ProductClassification(pred_probs) -> pd.DataFrame:
    pred_probs.columns = le.inverse_transform(pred_probs.columns)
    predicted_category = [pred_probs.columns[np.argmax(p)] for p in pred_probs.values]
    confidence = [np.max(p) for p in pred_probs.values]

    result = pd.DataFrame({
        "id": pred_probs.index,
        "ml_model_name": PRODUCT_CLASSIFICATION_MODEL,
        "predicted_category": predicted_category,
        "confidence": confidence,
        "all_predicted_probabilities": pred_probs.to_dict(orient='records')
    })

    return result


def eval_request(request_data):
    df = pd.read_json(request_data)

    if not set(PRODUCT_CLASSIFICATION_MODEL_FEATURES).issubset(set(df.columns)):
        logger.warning(
            f"The dataframe is missing features."
            f"Returning 'None'."
        )
        return None

    df = df.set_index("id")[PRODUCT_CLASSIFICATION_MODEL_FEATURES]
    return df


@app.route("/", methods=['POST'])
def product_classifier_handler() -> Response:
    """Reads the JSON data from the POST request, which is expected to include product data,
    which is used for inference.

    :return:
        A flask Response containing the predictions.
    """
    request_data = request.get_json()
    df = eval_request(request_data)
    pred_probs = predict_proba(df)

    result = create_ProductClassification(pred_probs)
    return Response(result.to_json(orient="records"), mimetype="application/json")


def create_app():
    serve(app, host="0.0.0.0", port=8282)
    return app
