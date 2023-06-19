import logging

from flask import Flask, Response, request
from product_classification.InferenceEngine import InferenceEngine
from product_classification.utils import to_df
from waitress import serve

from core.constants import PRODUCT_CLASSIFICATION_MODEL
from database.connection import GreenDB

app = Flask(__name__)

MODEL_DIR = f"/usr/src/app/data/models/{PRODUCT_CLASSIFICATION_MODEL}"

db_connection = GreenDB()
shop_thresholds = to_df(db_connection.get_latest_product_classification_thresholds())

IE = InferenceEngine(PRODUCT_CLASSIFICATION_MODEL, MODEL_DIR, shop_thresholds)

logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)


@app.route("/", methods=["POST"])
def product_classifier_handler() -> Response:
    """Reads the JSON data from the POST request, which is expected to include product data,
    which is used for inference.

    :return:
        A flask Response containing the predictions.
    """
    request_data = request.get_json()
    classification_df = IE.run_pipeline(request_data)

    return Response(classification_df.to_json(orient="records"), mimetype="application/json")


@app.route("/with_thresholds", methods=["POST"])
def thresholded_product_classifier_handler() -> Response:
    """Reads the JSON data from the POST request, which is expected to include product data,
    which is used for inference.

    :return:
        A flask Response containing the predictions.
    """
    request_data = request.get_json()
    classification_df = IE.run_pipeline(request_data, apply_shop_thresholds=True)

    return Response(classification_df.to_json(orient="records"), mimetype="application/json")


@app.route("/apply_thresholds", methods=["POST"])
def apply_thresholds_handler() -> Response:
    """Reads the JSON data from the POST request, which is expected to include product
    classifications products data with shops and merchants which is used for
    thresholding.

    :return:
        A flask Response containing the submitted product classifications with applied thresholds.
    """
    request_data = request.get_json()
    product_df = IE.eval_request(request_data.get("product_data"))
    classification_df = IE.eval_request(
        request_data.get("classification_data"), data_format="classifications"
    )

    classification_df = IE.apply_shop_thresholds(classification_df, product_df)

    return Response(classification_df.to_json(orient="records"), mimetype="application/json")


@app.route("/test", methods=["GET"])
def test() -> Response:
    """test endpoint used for test purposes and kubernetes readiness/liveness probes.

    :return:
        A flask Response containing the message: 'Successful'.
    """
    return Response("Successful!")


def create_app() -> Flask:
    serve(app, host="0.0.0.0", port=8282)
    return app
