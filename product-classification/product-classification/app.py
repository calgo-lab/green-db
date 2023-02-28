import json
from logging import getLogger

from flask import Flask, Response, request
from waitress import serve
import numpy as np
import pandas as pd
from autogluon.text import TextPredictor

logger = getLogger(__name__)

app = Flask(__name__)

classes = ['AUDIO HEADSETS', 'BLAZER', 'BLOUSE', 'CLOTHES WASHERS',
           'COOKER HOODS', 'DENIM_TROUSERS', 'DISHWASHERS', 'DRESSES',
           'FOOTWEAR', 'FREEZERS', 'JACKETS/CARDIGANS/WAISTCOATS',
           'OVENS', 'OVERALLS/BODYSUITS', 'PERSONAL CARRIERS',
           'PERSONAL COMPUTERS - PORTABLE', 'PRINTERS',
           'RANGE COOKERS/STOVES', 'REFRIGERATORS', 'RUCKSACK',
           'SHIRTS/POLO SHIRTS/T-SHIRTS', 'SKIRTS', 'SLEEPWEAR',
           'SLEEVELESS_SHIRT', 'SPIN/TUMBLE DRYERS', 'SWEATERS/PULLOVERS',
           'SWIMWEAR', 'TABLET PC', 'TRACKSUIT', 'TROUSERS/SHORTS', 'UNDERWEAR']

features = ["name", "description"]

MODEL_DIR = "/usr/src/app/data/models/DE-GB-FR-zalando-asos-otto-hm-amazon-microsoft-mdeberta-v3" \
            "-base-name-description-misty-snowflake-210"


@app.route("/", methods=['POST'])
def product_classifier_handler() -> Response:
    """Reads the JSON data from the POST request, which is expected to include product data,
    which is used for inference.

    :return:
        A flask Response containing the predictions.
    """

    request_data = request.get_json()
    df = pd.read_json(request_data)

    model = TextPredictor.load(MODEL_DIR)

    if not set(features).issubset(set(df.columns)):
        logger.warning(
            f"The dataframe is missing features."
            f"Returning an empty result."
        )
        return Response({}, mimetype="application/json")

    pred_probs = model.predict_proba(df)
    pred_probs.columns = classes
    predicted_category = [classes[np.argmax(p)] for p in pred_probs.values]
    confidence = [np.max(p) for p in pred_probs.values]

    # TODO: add label qualities via cleanlab as well (needs mapping from GreenDB to GPC)
    # drop new categories or incorporate into existing
    # return label for products with multiple categories
    # return label for misclassified

    data = {
        "pred_probs": pred_probs.to_dict(),
        "predictions": predicted_category,
        "confidence": str(confidence),
    }

    return Response(json.dumps(data), mimetype="application/json")


@app.route("/test", methods=['GET'])
def test() -> Response:
    return Response("test")


def create_app():
    serve(app, host="0.0.0.0", port=8282)
    return app
