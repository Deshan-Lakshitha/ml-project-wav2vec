# -*- coding: utf-8 -*-
"""wav2vec_layer_12_new.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16XR7fa-7wS3l-eJjsr255pl6yh64LeVu
"""

from google.colab import drive

drive.mount("/content/drive")

"""## Imports

"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder

from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import SelectKBest, f_classif

import xgboost as xgb
from catboost import CatBoostClassifier

import matplotlib.pyplot as plt
import seaborn as sn

from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

import time

import joblib

"""## Load dataset and create dataframes

"""

# Load datasets
train_df = pd.read_csv("../../datasets/layer-12/train.csv")
valid_df = pd.read_csv("../../datasets/layer-12/valid.csv")
test_df = pd.read_csv("../../datasets/layer-12/test.csv")

train_df.shape, valid_df.shape, test_df.shape

"""## For each label, seperate feature data

"""

labels = ["label_1", "label_2", "label_3", "label_4"]

X_train = {}
X_valid = {}
X_test = {}
y_train = {}
y_valid = {}

for label in labels:
    # Standardize the feature columns
    scaler = StandardScaler()
    tr_df = train_df
    val_df = valid_df
    tst_df = test_df
    if label == "label_2":  # Remove NaN rows for label_2
        tr_df = train_df[train_df[label].notna()]
        val_df = valid_df[valid_df[label].notna()]

    X_train[label] = pd.DataFrame(scaler.fit_transform(tr_df.iloc[:, :-4]))
    X_valid[label] = pd.DataFrame(scaler.transform(val_df.iloc[:, :-4]))
    X_test[label] = pd.DataFrame(scaler.transform(tst_df.iloc[:, :-4]))

    # Ensure you keep the target labels as separate DataFrames
    y_train[label] = tr_df[label]
    y_valid[label] = val_df[label]

"""## Feature Selection

"""

X_train_selected = {}
X_valid_selected = {}
X_test_selected = {}

"""Feature selection for each label

"""

def feature_selection(L):
    # Figure label frequencies
    plt.figure(figsize=(15, 6))
    sn.countplot(data=y_train, x=L, color="green")

    k = (
        350
        if L == labels[0]
        else (350 if L == labels[1] else 350 if L == labels[3] else 350)
    )

    selector = SelectKBest(f_classif, k=k)

    X_train_selected[L] = pd.DataFrame(
        selector.fit_transform(X_train[label], y_train[label])
    )
    X_valid_selected[L] = pd.DataFrame(selector.transform(X_valid[label]))
    X_test_selected[L] = pd.DataFrame(selector.transform(X_test[label]))

for label in labels:
    feature_selection(label)

X_train_selected["label_4"].shape

X_valid_selected["label_1"].shape

X_test_selected["label_3"].shape

"""## Dimensionality reduction using PCA

"""

X_train_pca = {}
X_valid_pca = {}
X_test_pca = {}

from sklearn.decomposition import PCA


def PCA_reduction(L, X_train, X_valid):
    n_components = 0.99 if L == labels[1] else 0.95

    # Fit PCA on the training data
    pca = PCA(n_components=n_components)
    X_train_pca[L] = pca.fit_transform(X_train[L])

    # Transform validation and test data using the same PCA
    X_valid_pca[L] = pca.transform(X_valid[L])
    X_test_pca[L] = pca.transform(X_test[L])

for label in labels:
    PCA_reduction(label, X_train, X_valid)

X_train_pca["label_1"].shape

"""## Hyperparameter Tuning with Cross validation

"""

models = ["svm", "catboost"]

# Model hyperparameters
param_dist_svm = {
    "C": np.logspace(-3, 3, 6),
    "kernel": ["linear", "rbf", "poly"],
    "gamma": ["scale", "auto"] + list(np.logspace(-3, 3, 5)),
}

param_dist_catboost = {
    "learning_rate": [0.01, 0.1, 0.3],  # Learning rate values
    "depth": [4, 6, 8],                # Depth of the trees
    "iterations": [100, 200],          # Number of boosting iterations
}

def best_classifier(model, L, X_train, y_train, random_state, n_iter, n_jobs, cv=2):
    t1 = time.time()
    classifier = None
    class_weight = None if L == labels[0] else "balanced"
    param_dist = None

    if model == models[0]:
        # Create an SVM classifier
        classifier = SVC(class_weight=class_weight)
        param_dist = param_dist_svm
    elif model == models[1]:
        # Create an random forest classifier
        classifier = CatBoostClassifier(verbose=False)
        param_dist = param_dist_catboost

    # Perform Random Search for each model
    random_search = RandomizedSearchCV(
        classifier,
        param_distributions=param_dist,
        scoring="accuracy",
        cv=cv,
        verbose=1,
        random_state=random_state,
        n_iter=n_iter,
        n_jobs=n_jobs,
    )
    print(
        "===========================Random search fit started================================"
    )
    random_search.fit(X_train[L], y_train[L])
    print(
        "===========================Random search fit stopped================================"
    )
    classifier = random_search.best_estimator_  # Get best classifier from random search
    print(f"Best Parameters for {model}:")
    print(random_search.best_params_)
    print(f"Best Accuracy for {model}:")
    print(random_search.best_score_)

    t2 = time.time()
    print(f"Time elapsed: {(t2-t1)/60}mins")

    return classifier

## Tuning label_1 with svm
l1_best_model = best_classifier(
    models[0], labels[0], X_train_pca, y_train, random_state=42, n_iter=5, n_jobs=1
)

## Tuning label_3 with svm
l3_best_model = best_classifier(
    models[0], labels[2], X_train_pca, y_train, random_state=42, n_iter=5, n_jobs=1
)

## Tuning label_2 with svm
l2_best_model = best_classifier(
    models[0], labels[1], X_train_pca, y_train, random_state=42, n_iter=5, n_jobs=1
)

## Tuning label_4 with svm
l4_best_model = best_classifier(
    models[0], labels[3], X_train_pca, y_train, random_state=42, n_iter=5, n_jobs=1
)

joblib.dump(l1_best_model, 'l1_best_model_svm_cv')
joblib.dump(l2_best_model, 'l2_best_model_svm_cv')
joblib.dump(l3_best_model, 'l3_best_model_svm_cv')
joblib.dump(l4_best_model, 'l4_best_model_svm_cv')

"""## Evaluations"""

def svm_evaluate(classifier, L, X_train, X_valid, y_train, y_valid):
    classifier.fit(X_train[L], y_train[L])

    y_pred = classifier.predict(X_valid[L])
    accuracy = accuracy_score(y_valid[L], y_pred)
    print(f"SVM Validation Accuracy Score for {L} = ", accuracy)

"""#### Before feature engineering

"""

l1_model = classifier(models[0], labels[0], X_train, X_valid, y_train, y_valid)

l2_model = classifier(models[0], labels[1], X_train, X_valid, y_train, y_valid)

l3_model = classifier(models[0], labels[2], X_train, X_valid, y_train, y_valid)

l4_model = classifier(models[0], labels[3], X_train, X_valid, y_train, y_valid)

"""#### _After_ dimension reduction

"""

# Load saved best models
l1_best_model = joblib.load('l1_best_model_svm_cv')
l2_best_model = joblib.load('l2_best_model_svm_cv')
l3_best_model = joblib.load('l3_best_model_svm_cv')
l4_best_model = joblib.load('l4_best_model_svm_cv')

svm_evaluate(l1_best_model, labels[0], X_train_pca, X_valid_pca, y_train, y_valid)

svm_evaluate(l2_best_model, labels[1], X_train_pca, X_valid_pca, y_train, y_valid)

svm_evaluate(l3_best_model, labels[2], X_train_pca, X_valid_pca, y_train, y_valid)

svm_evaluate(l4_best_model, labels[3], X_train_pca, X_valid_pca, y_train, y_valid)

"""## Predictions

Label 1 prediction
"""

# Predict using best SVM model for label 1
y_pred_l1 = l1_best_model.predict(X_test_pca[labels[0]])

# Predict using best SVM model for label 1
y_pred_l2 = l2_best_model.predict(X_test_pca[labels[1]])

# Predict using best SVM model for label 1
y_pred_l3 = l3_best_model.predict(X_test_pca[labels[2]])

# Predict using best SVM model for label 1
y_pred_l4 = l4_best_model.predict(X_test_pca[labels[3]])

"""## Generate Output CSV Files

Convert predicted label arrays to dataframes
"""

id_column = test_df.iloc[:, :1]
y_pred_l1 = pd.DataFrame(y_pred_l1)
y_pred_l2 = pd.DataFrame(y_pred_l2)
y_pred_l3 = pd.DataFrame(y_pred_l3)
y_pred_l4 = pd.DataFrame(y_pred_l4)

"""Add colun names

"""

y_pred_l1.columns = [labels[0]]
y_pred_l2.columns = [labels[1]]
y_pred_l3.columns = [labels[2]]
y_pred_l4.columns = [labels[3]]

pd.DataFrame(id_column)

"""Generate submission file

"""

output_dataframe = pd.concat(
    [id_column, y_pred_l1, y_pred_l2, y_pred_l3, y_pred_l4], axis=1
)

output_dataframe

output_dataframe.to_csv("output.csv", index=False)

"""## Use hyperparameter tuned models"""

def evaluate(classifier, x, y, L):
    y_pred = classifier.predict(x[L])
    accuracy = accuracy_score(y[L], y_pred)
    print(f"SVM Validation Accuracy Score for {L} = ", accuracy)

"""Label 1<br>
Best Parameters for svm:
{'kernel': 'poly', 'gamma': 0.03162277660168379, 'C': 1000.0}
"""

l1_best_model = SVC(class_weight=None, kernel='poly', gamma=0.03162277660168379, C=1000.0)

l1_best_model.fit(X_train_pca[labels[0]], y_train[labels[0]])

evaluate(l1_best_model, X_valid_pca, y_valid, labels[0])

"""Label 2<br>
Best Parameters for svm:
{'kernel': 'poly', 'gamma': 0.03162277660168379, 'C': 1000.0}
"""

l2_best_model = SVC(class_weight=None, kernel='poly', gamma=0.03162277660168379, C=1000.0)

l2_best_model.fit(X_train_pca[labels[1]], y_train[labels[1]])

evaluate(l2_best_model, X_valid_pca, y_valid, labels[1])

"""Label 3<br>
Best Parameters for svm:
{'kernel': 'poly', 'gamma': 0.03162277660168379, 'C': 1000.0}
"""

l3_best_model = SVC(class_weight=None, kernel='poly', gamma=0.03162277660168379, C=1000.0)

l3_best_model.fit(X_train_pca[labels[2]], y_train[labels[2]])

evaluate(l3_best_model, X_valid_pca, y_valid, labels[2])

"""Label 4<br>
Best Parameters for svm:
{'kernel': 'rbf', 'gamma': 'auto', 'C': 3.981071705534969}
"""

l4_best_model = SVC(class_weight=None, kernel='rbf', gamma='auto', C=3.981071705534969)

l4_best_model.fit(X_train_pca[labels[3]], y_train[labels[3]])

evaluate(l4_best_model, X_valid_pca, y_valid, labels[3])

"""Save models"""

joblib.dump(l1_best_model, '../../saved_models/layer_12/l1_best_model')
joblib.dump(l2_best_model, '../../saved_models/layer_12/l2_best_model')
joblib.dump(l3_best_model, '../../saved_models/layer_12/l3_best_model')
joblib.dump(l4_best_model, '../../saved_models/layer_12/l4_best_model')

"""## Predictions for valid set"""

y_pred_valid_set_l1 = l1_best_model.predict(X_valid_pca[labels[0]])
y_pred_valid_set_l2 = l2_best_model.predict(X_valid_pca[labels[1]])
y_pred_valid_set_l3 = l3_best_model.predict(X_valid_pca[labels[2]])
y_pred_valid_set_l4 = l4_best_model.predict(X_valid_pca[labels[3]])

# save to csv
y_pred_valid_set_l1 = pd.DataFrame(y_pred_valid_set_l1)
y_pred_valid_set_l2 = pd.DataFrame(y_pred_valid_set_l2)
y_pred_valid_set_l3 = pd.DataFrame(y_pred_valid_set_l3)
y_pred_valid_set_l4 = pd.DataFrame(y_pred_valid_set_l4)

y_pred_valid_set_l1.to_csv("y_pred_valid_set_l1.csv", index=False)
y_pred_valid_set_l2.to_csv("y_pred_valid_set_l2.csv", index=False)
y_pred_valid_set_l3.to_csv("y_pred_valid_set_l3.csv", index=False)
y_pred_valid_set_l4.to_csv("y_pred_valid_set_l4.csv", index=False)

