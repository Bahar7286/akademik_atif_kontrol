import xgboost as xgb
import pickle

def load_model(path="models/xgboost_model.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)

def predict(features):
    model = load_model()
    return model.predict([features])[0]