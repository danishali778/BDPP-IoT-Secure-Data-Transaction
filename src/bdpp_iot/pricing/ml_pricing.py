from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


FEATURE_COLUMNS = [
    "data_type",
    "integrity_score",
    "freshness",
    "market_demand",
    "seller_reputation",
    "data_volume",
    "access_frequency",
]


class StaticPricingModel:
    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        type_weight = frame["data_type"].map(
            {
                "heart_rate": 1.0,
                "temperature": 0.9,
                "blood_pressure": 1.1,
                "glucose": 1.2,
            }
        ).fillna(1.0)
        return (
            55.0
            * type_weight.to_numpy()
            * frame["integrity_score"].to_numpy()
            * (0.5 + frame["market_demand"].to_numpy())
            * (0.5 + frame["seller_reputation"].to_numpy())
        )


class MLPricingModel:
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.model = RandomForestRegressor(
            n_estimators=160,
            max_depth=10,
            min_samples_leaf=3,
            random_state=seed,
        )
        self.columns_: list[str] | None = None

    def _features(self, frame: pd.DataFrame) -> pd.DataFrame:
        encoded = pd.get_dummies(frame[FEATURE_COLUMNS], columns=["data_type"], drop_first=False)
        if self.columns_ is None:
            self.columns_ = list(encoded.columns)
        return encoded.reindex(columns=self.columns_, fill_value=0)

    def fit(self, frame: pd.DataFrame) -> None:
        x = self._features(frame)
        y = frame["final_price"].to_numpy()
        self.model.fit(x, y)

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        x = self._features(frame)
        return self.model.predict(x)


def evaluate_pricing(history: pd.DataFrame, seed: int, test_fraction: float) -> dict:
    train, test = train_test_split(history, test_size=test_fraction, random_state=seed)

    static_model = StaticPricingModel()
    static_pred = static_model.predict(test)

    ml_model = MLPricingModel(seed=seed)
    ml_model.fit(train)
    ml_pred = ml_model.predict(test)

    actual = test["final_price"].to_numpy()
    static_rmse = float(np.sqrt(mean_squared_error(actual, static_pred)))
    ml_rmse = float(np.sqrt(mean_squared_error(actual, ml_pred)))

    return {
        "static_mae": float(mean_absolute_error(actual, static_pred)),
        "ml_mae": float(mean_absolute_error(actual, ml_pred)),
        "static_rmse": static_rmse,
        "ml_rmse": ml_rmse,
        "static_r2": float(r2_score(actual, static_pred)),
        "ml_r2": float(r2_score(actual, ml_pred)),
        "test_frame": test.reset_index(drop=True),
        "static_pred": static_pred,
        "ml_pred": ml_pred,
        "actual": actual,
    }
