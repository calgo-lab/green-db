import numpy as np
import pandas as pd
from core.constants import PRODUCT_CLASSIFICATION_MODEL
from core.product_classification_thresholds.bootstrap_database import thresholds

from product_classification.InferenceEngine import InferenceEngine
from product_classification.utils import to_df

shop_thresholds = to_df(thresholds)

MODEL_DIR = f"/usr/src/app/data/models/{PRODUCT_CLASSIFICATION_MODEL}"
IE = InferenceEngine(PRODUCT_CLASSIFICATION_MODEL, MODEL_DIR, shop_thresholds)

product_json = '{"description":{"0":"blue sneakers"},"id":{"0":0},"name":{"0":"sneakers blue"}}'
products_json = (
    '{"id":{"0":0,"1":1},"name":{"0":"sneakers blue","1":"t-shirt red"},'
    '"description":{"0":"blue sneakers ","1":"red t-shirt"}}'
)

product_pred_probs = (
    '{"0":{"0":0.0000011791},"1":{"0":0.0000001763},"2":{"0":0.000000055},'
    '"3":{"0":0.0000001777},"4":{"0":0.0000013303},"5":{"0":0.0000008797},'
    '"6":{"0":0.0000004024},"7":{"0":0.0000001178},"8":{"0":0.0000003841},'
    '"9":{"0":0.0000001193},"10":{"0":0.0000000448},"11":{"0":0.0000010104},'
    '"12":{"0":0.0000008012},"13":{"0":0.0000006439},"14":{"0":0.0000001045},'
    '"15":{"0":0.0000003427},"16":{"0":0.0000011422},"17":{"0":0.000000192},'
    '"18":{"0":0.0000000079},"19":{"0":0.0000000173},"20":{"0":0.0000000576},'
    '"21":{"0":0.0000013447},"22":{"0":0.0000000906},"23":{"0":0.0000000673},'
    '"24":{"0":0.0000064224},"25":{"0":0.0000001808},"26":{"0":0.0000002557},'
    '"27":{"0":0.000000161},"28":{"0":0.0000004912},"29":{"0":0.9999747276},'
    '"30":{"0":0.0000023699},"31":{"0":0.0000001294},"32":{"0":0.0000003844},'
    '"33":{"0":0.0000003245},"34":{"0":0.0000004584},"35":{"0":0.0000007302},'
    '"36":{"0":0.0000001338},"37":{"0":0.0000000956},"38":{"0":0.0000002152},'
    '"39":{"0":0.000001542},"40":{"0":0.0000004811},"41":{"0":0.000000024},'
    '"42":{"0":0.000000162}}'
)


def test_eval_product_request():
    df = IE.eval_request(product_json)
    assert df.shape == (1, 2)


def test_eval_products_request():
    df = IE.eval_request(products_json)
    assert df.shape == (2, 2)


def prep_pred_probs():
    actual_probs = pd.read_json(product_pred_probs)
    actual_probs.columns = IE.classes
    actual_probs = actual_probs.to_dict(orient="records")

    return pd.DataFrame(
        {
            "id": 0,
            "ml_model_name": PRODUCT_CLASSIFICATION_MODEL,
            "predicted_category": "SNEAKERS",
            "confidence": 0.9999747276,
            "all_predicted_probabilities": actual_probs,
        }
    )


def test_convert_pred_probs():
    product_classification = prep_pred_probs()
    pcl = IE.probas_to_ProductClassifications(pd.read_json(product_pred_probs))
    rows, cols = product_classification.shape
    for row in range(rows):
        for col in range(cols):
            if isinstance(product_classification.iloc[row, col], float):
                assert np.isclose(product_classification.iloc[row, col], pcl.iloc[row, col])
            else:
                assert product_classification.iloc[row, col] == pcl.iloc[row, col]


def test_above_thresholding():
    pc_above_thresh = prep_pred_probs()
    thresholded = IE.apply_shop_thresholds(pc_above_thresh)
    # check for using minimal fallback threshold
    assert np.isclose(0.9996114373207092, thresholded.loc[0, "threshold"])
    assert thresholded.loc[0, "category_thresholded"] == "SNEAKERS"


def test_below_thresholding():
    pc_below_thresh = prep_pred_probs()
    # manipulate original confidence with a value below the threshold value
    pc_below_thresh["confidence"] = 0.995
    thresholded_below = IE.apply_shop_thresholds(pc_below_thresh)
    assert thresholded_below.loc[0, "category_thresholded"] == "under_threshold"


def test_shop_thresholding():
    pc = prep_pred_probs()
    p = IE.eval_request(product_json)
    p["merchant"] = "otto"
    p["source"] = "otto"
    thresholded = IE.apply_shop_thresholds(pc, p)
    assert np.isclose(0.999751627445221, thresholded.loc[0, "threshold"])
    assert thresholded.loc[0, "category_thresholded"] == "SNEAKERS"


def test_threshold_existence_per_category():
    assert set(IE.shop_thresholds["predicted_category"].unique()) == set(IE.classes)
