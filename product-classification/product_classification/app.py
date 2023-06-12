import logging
from typing import Optional

import numpy as np
import pandas as pd
from autogluon.multimodal import MultiModalPredictor
from flask import Flask, Response, request
from product_classification.utils import to_df
from sklearn.preprocessing import LabelEncoder
from waitress import serve

from core.constants import PRODUCT_CLASSIFICATION_MODEL, PRODUCT_CLASSIFICATION_MODEL_FEATURES
from core.domain import ProductClassification
from database.connection import GreenDB

logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)

app = Flask(__name__)

model_classes = [
    "BACKPACK",
    "BAG",
    "BLOUSE",
    "COOKER_HOOD",
    "DESKTOP_PC",
    "DISHWASHER",
    "DRESS",
    "DRYER",
    "FREEZER",
    "FRIDGE",
    "GAMECONSOLE",
    "HEADPHONES",
    "HEADSET",
    "JACKET",
    "JEANS",
    "LAPTOP",
    "LINEN",
    "MONITOR",
    "NIGHTWEAR",
    "OVEN",
    "OVERALL",
    "PANTS",
    "PRINTER",
    "SHIRT",
    "SHOES",
    "SHORTS",
    "SKIRT",
    "SMARTPHONE",
    "SMARTWATCH",
    "SNEAKERS",
    "SOCKS",
    "STOVE",
    "SUIT",
    "SWEATER",
    "SWIMWEAR",
    "TABLET",
    "TOP",
    "TOWEL",
    "TRACKSUIT",
    "TSHIRT",
    "TV",
    "UNDERWEAR",
    "WASHER",
]

le = LabelEncoder()
le.fit(model_classes)

MODEL_DIR = f"/usr/src/app/data/models/{PRODUCT_CLASSIFICATION_MODEL}"

db_connection = GreenDB()
shop_thresholds = to_df(db_connection.get_latest_product_classification_thresholds())

model = MultiModalPredictor.load(MODEL_DIR)
model.set_num_gpus(0)


def predict_proba(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is used to perform inference on the retrieved products.

    Args:
        df (pd.Dataframe): Dataframe with Product instances.

    Returns:
        pd.DataFrame: pd.DataFrame with predicted probabilites for each product category /
        model_class.
    """

    logger.info(f"Predicting for {len(df)} products ...")
    probas = model.predict_proba(df)
    logger.info("Finished prediction.")
    return probas


def join_features_with_inference(
    product_df: pd.DataFrame, classification_df: pd.DataFrame
) -> pd.DataFrame:
    """
    This function is used to join the product dataframe with the retrieved classification Dataframe.

    Args:
        product_df (pd.Dataframe): Dataframe with product instances.
        classification_df (pd.Dataframe): Dataframe with ProductClassification instances.

    Returns:
        pd.DataFrame: pd.DataFrame of ProductClassification objects with thresholded
        categories and corresponding thresholds.
    """

    return classification_df.join(product_df, on="id")


def apply_shop_thresholds(
    classification_df: pd.DataFrame,
    shop_thresholds: pd.DataFrame,
    product_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    This function is used to apply thresholds on the predictions to exclude out-of-distribution
    products.

    Args:
        product_df (pd.Dataframe): Dataframe with product instances.
        classification_df (pd.Dataframe): Dataframe with ProductClassification instances.

    Returns:
        pd.DataFrame: pd.DataFrame of ProductClassification objects with thresholded
        categories and corresponding thresholds.
    """

    # add fallback threshold if a shop/category was not present during evaluation
    # use smallest threshold from all shops as fallback
    fallback_thresh_by_category = (
        shop_thresholds.groupby("predicted_category")["threshold"].agg(min).to_dict()
    )
    fallback_thresholds = classification_df["predicted_category"].apply(
        lambda x: fallback_thresh_by_category.get(x)
    )

    # set shop specific thresholds if source and merchant are sent along with request
    if product_df is not None and {"source", "merchant"}.issubset(set(product_df.columns)):
        combined = join_features_with_inference(product_df, classification_df)
        join_keys = ["ml_model_name", "source", "merchant", "predicted_category"]
        combined = combined.join(shop_thresholds.set_index(join_keys), on=join_keys)
        combined["threshold"].fillna(fallback_thresholds)
    else:
        combined = pd.concat([classification_df, fallback_thresholds.rename("threshold")], axis=1)

    combined["category_thresholded"] = combined.apply(
        lambda x: x["predicted_category"]
        if x["confidence"] >= x["threshold"]
        else "under_threshold",
        axis=1,
    )

    return combined[list(classification_df.columns) + ["category_thresholded", "threshold"]]


def probas_to_ProductClassifications(probas: pd.DataFrame) -> pd.DataFrame:
    """
    This function is used to transform predicted probabilities into a DataFrame with complete
    ProductClassification objects.

    Args:
        probas (pd.Dataframe): Dataframe with predicted probabilities.

    Returns:
        pd.DataFrame: pd.DataFrame of ProductClassification objects.
    """

    probas.columns = le.inverse_transform(probas.columns)
    predicted_category = [probas.columns[np.argmax(p)] for p in probas.values]
    confidence = [np.max(p) for p in probas.values]

    result = pd.DataFrame(
        {
            "id": probas.index,
            "ml_model_name": PRODUCT_CLASSIFICATION_MODEL,
            "predicted_category": predicted_category,
            "confidence": confidence,
            "all_predicted_probabilities": probas.to_dict(orient="records"),
        }
    )

    return result


def eval_request(request_data: str, data_format: str = "products") -> Optional[pd.DataFrame]:
    """
    This function is used to evaluate the data of the request and checks whether all necessary
    columns/features are part of the request data.

    Args:
        request_data (str): data which was sent along the POST request with a string in JSON format.
        data_format (str): format to use for evaluating the request data. Either 'products' or
        'classifications'.


    Returns:
        Optional(pd.DataFrame): pd.DataFrame of the request data.
    """

    df = pd.read_json(request_data)

    if data_format == "products":
        required_columns = PRODUCT_CLASSIFICATION_MODEL_FEATURES + ["id"]
    elif data_format == "classifications":
        required_columns = ProductClassification.__fields__.keys()
    else:
        return None

    if not set(required_columns).issubset(set(df.columns)):
        logger.warning(
            f"The dataframe is missing features. Make sure it includes the following columns: "
            f"{required_columns}. Returning 'None'."
        )
        return None

    df = df.set_index("id")
    return df


def run_pipeline(request_data: str, apply_thresholds: bool = False) -> pd.DataFrame:
    """The standard pipeline to run for evaluating the request data and performing inference.

    Args:
    request_data (json): data which was sent along the POST request. Should include a
    pd.DataFrame that was transformed into serialized json format.
    data_format (str): format to use for evaluating the request data. Either 'products' or
    'classifications'.

    :return:
        A flask Response containing the predictions.
    """
    df = eval_request(request_data)
    pred_probs = predict_proba(df)

    classification_df = probas_to_ProductClassifications(pred_probs)
    if apply_thresholds:
        classification_df = apply_shop_thresholds(classification_df, shop_thresholds, df)

    return classification_df


@app.route("/", methods=["POST"])
def product_classifier_handler() -> Response:
    """Reads the JSON data from the POST request, which is expected to include product data,
    which is used for inference.

    :return:
        A flask Response containing the predictions.
    """
    request_data = request.get_json()
    classification_df = run_pipeline(request_data)

    return Response(classification_df.to_json(orient="records"), mimetype="application/json")


@app.route("/with_thresholds", methods=["POST"])
def thresholded_product_classifier_handler() -> Response:
    """Reads the JSON data from the POST request, which is expected to include product data,
    which is used for inference.

    :return:
        A flask Response containing the predictions.
    """
    request_data = request.get_json()
    classification_df = run_pipeline(request_data, apply_thresholds=True)

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
    product_df = eval_request(request_data.get("product_data"))
    classification_df = eval_request(
        request_data.get("classification_data"), data_format="classifications"
    )

    classification_df = apply_shop_thresholds(classification_df, shop_thresholds, product_df)

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
