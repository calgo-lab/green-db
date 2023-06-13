import logging
from typing import Optional

import numpy as np
import pandas as pd
from autogluon.multimodal import MultiModalPredictor
from core.constants import PRODUCT_CLASSIFICATION_MODEL_FEATURES
from core.domain import ProductClassification
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MODEL_CLASSES = [
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
le.fit(MODEL_CLASSES)


class InferenceEngine:
    """A class to load the XLM from autogluon and perform inference."""

    def __init__(self, model_name, model_path, shop_thresholds):
        """
        :param model_path: The path to the model on the system.
        :param shop_thresholds: The thresholds for each shop to use for thresholding.
        """
        self.name = model_name
        self.path = model_path
        self.shop_thresholds = shop_thresholds
        self.classes = MODEL_CLASSES
        self.model = None

    def load_model(self):
        self.model = MultiModalPredictor.load(self.model_path)
        self.model.set_num_gpus(0)

    def predict_proba(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This function is used to perform inference on the retrieved products.

        Args:
            df (pd.Dataframe): Dataframe with Product instances.

        Returns:
            pd.DataFrame: pd.DataFrame with predicted probabilites for each product category /
            model_class.
        """
        probas = self.model.predict_proba(df)
        return probas

    @staticmethod
    def join_features_with_inference(
        product_df: pd.DataFrame, classification_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        This function is used to join the product dataframe with the retrieved classification
        Dataframe.

        Args:
            product_df (pd.Dataframe): Dataframe with product instances.
            classification_df (pd.Dataframe): Dataframe with ProductClassification instances.

        Returns:
            pd.DataFrame: pd.DataFrame of ProductClassification objects with thresholded
            categories and corresponding thresholds.
        """

        return classification_df.join(product_df, on="id")

    def apply_shop_thresholds(
        self,
        classification_df: pd.DataFrame,
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
            self.shop_thresholds.groupby("predicted_category")["threshold"].agg(min).to_dict()
        )
        fallback_thresholds = classification_df["predicted_category"].apply(
            lambda x: fallback_thresh_by_category.get(x)
        )

        # set shop specific thresholds if source and merchant are sent along with request
        if product_df is not None and {"source", "merchant"}.issubset(set(product_df.columns)):
            combined = self.join_features_with_inference(product_df, classification_df)
            join_keys = ["ml_model_name", "source", "merchant", "predicted_category"]
            combined = combined.join(self.shop_thresholds.set_index(join_keys), on=join_keys)
            combined["threshold"].fillna(fallback_thresholds)
        else:
            combined = pd.concat(
                [classification_df, fallback_thresholds.rename("threshold")], axis=1
            )

        combined["category_thresholded"] = combined.apply(
            lambda x: x["predicted_category"]
            if x["confidence"] >= x["threshold"]
            else "under_threshold",
            axis=1,
        )

        return combined[list(classification_df.columns) + ["category_thresholded", "threshold"]]

    def probas_to_ProductClassifications(self, probas: pd.DataFrame) -> pd.DataFrame:
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
                "ml_model_name": self.name,
                "predicted_category": predicted_category,
                "confidence": confidence,
                "all_predicted_probabilities": probas.to_dict(orient="records"),
            }
        )

        return result

    def run_pipeline(self, request_data: str, apply_thresholds: bool = False) -> pd.DataFrame:
        """The standard pipeline to run for evaluating the request data and performing inference.

        Args:
        request_data (json): data which was sent along the POST request. Should include a
        pd.DataFrame that was transformed into serialized json format.
        data_format (str): format to use for evaluating the request data. Either 'products' or
        'classifications'.

        :return:
            A flask Response containing the predictions.
        """
        df = self.eval_request(request_data)
        pred_probs = self.model.predict_proba(df)

        classification_df = self.probas_to_ProductClassifications(pred_probs)
        if apply_thresholds:
            classification_df = self.apply_shop_thresholds(classification_df, df)

        return classification_df

    @staticmethod
    def eval_request(request_data: str, data_format: str = "products") -> Optional[pd.DataFrame]:
        """
        This function is used to evaluate the data of the request and checks whether all necessary
        columns/features are part of the request data.

        Args: request_data (str): data which was sent along the POST request with a string in
        JSON format. data_format (str): format to use for evaluating the request data. Either
        'products' or 'classifications'.


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
