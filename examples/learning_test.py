"""
The goal of this file was to understand why the ML algorithms weren't able to learn the strokes.
As it turns out, the frequency of strokes was too low in the learn set.
"""
import numpy as np
from sklearn import linear_model
from sklearn import ensemble
from sklearn import neural_network

from learning.confusion_matrix import ConfusionMatrix


def calculate_stroke_risk(score):
    """ Numbers according to the Swedish Atrial Fibrillation Cohort Study """
    if score == 0:
        stroke_risk = 0.002
    elif score == 1:
        stroke_risk = 0.006
    elif score == 2:
        stroke_risk = 0.022
    elif score == 3:
        stroke_risk = 0.032
    elif score == 4:
        stroke_risk = 0.048
    elif score == 5:
        stroke_risk = 0.072
    elif score == 6:
        stroke_risk = 0.092
    elif score == 7:
        stroke_risk = 0.112
    elif score == 8:
        stroke_risk = 0.108
    else:
        stroke_risk = 0.122
    
    return stroke_risk
        

def calculate_chads_vasc(diseases, gender, age):
    """
    First element of diseases should be stroke, order of the rest doesn't really matter
    Assuming gender value of 1 is female, 0 is male
    """
    weights = [2, 1, 1, 1, 1]

    return sum(np.array(diseases) * np.array(weights)) + (65 <= age < 75) + 2 * (75 <= age) + gender


def chads_vasc_prediction(feature_matrix):
    predictions = []

    for vector in feature_matrix:
        diseases = vector[:5]
        age = vector[-1]
        gender = vector[-2]

        score = calculate_chads_vasc(diseases, gender, age)
        predictions.append(score >= 3)

    return predictions


def random_prediction(n):
    return [1 if v <= 0.02 else 0 for v in np.random.random_sample(n).tolist()]


def create_data():
    """
    Feature Vector: index, variable, value and distribution
    0   S   0-1     90/10
    1   H   0-1     90/10
    2   D   0-1     90/10
    3   C   0-1     90/10
    4   V   0-1     90/10
    5   Sc  0-1     50/50
    6   A   45-105  uniform 
    """
    """  Generate 5 variables for the 5 different diseases with a 90/10 split """
    diseases = [1 if v > 0.90 else 0 for v in np.random.random_sample(5).tolist()]

    """  Generate a uniformly distributed age between 45 and 105 """
    age = round((np.random.random_sample() / 2) * 100 + 45)

    """  Randomly generate a gender, assuming 1 is female, 0 is male """
    gender = 1 if np.random.random_sample() >= 0.5 else 0

    """  Put all the features in a list """
    features = diseases + [gender, age]

    """  Calculate the CHADS-VASc score to find a more correct stroke risk """
    score = calculate_chads_vasc(diseases, gender, age)
    stroke_risk = calculate_stroke_risk(score)

    """  Randomly assign a stroke to this patient based on its stroke risk """
    target = 1 if np.random.random_sample() < stroke_risk else 0

    return features, target


def main():
    samples = 100000
    test_rate = 0.3

    """  Generate data """
    X = []
    t = []
    for i in range(samples):
        features, target = create_data()
        X.append(features)
        t.append(target)

    """  Split data in test and learn sets """
    # split = round(samples * test_rate)
    # X_learn = X[split:]
    # t_learn = t[split:]
    # X_test = X[:split]
    # t_test = t[:split]
    strokes_indices = [i for i, v in enumerate(t) if v]

    learn_size = len(strokes_indices)

    learn_indices = strokes_indices[len(strokes_indices) // 2:]
    for i in range(len(t)):
        if i not in strokes_indices:
            learn_indices.append(i)
        if len(learn_indices) >= learn_size:
            break
    X_learn = [X[i] for i in learn_indices]
    t_learn = [t[i] for i in learn_indices]
    X_test = [X[i] for i in range(len(X)) if i not in learn_indices]
    t_test = [t[i] for i in range(len(t)) if i not in learn_indices]

    """  Use Random Forest or Logistic Regression to learn and predict the strokes """
    clf = ensemble.RandomForestClassifier(n_estimators=100, n_jobs=-1)
    # clf = linear_model.LogisticRegression()
    clf.fit(X_learn, t_learn)
    ml_prediction = clf.predict(X_test)
    """  Compare the results with the target vector """
    ml_cm = ConfusionMatrix(t_test, ml_prediction, name="Machine Learning")

    """  Use the CHADS-VASc model to predict strokes """
    chads_vasc_predictions = chads_vasc_prediction(X_test)
    """  Compare the results with the target vector """
    chads_vasc_cm = ConfusionMatrix(t_test, chads_vasc_predictions, name="CHADS-VASc")

    """  Randomly predict stroke based on only the base stroke rate """
    #  random_predictions = random_prediction(len(X_test))
    """  Compare the results with the target vector """
    #  random_cm = ConfusionMatrix(t_test, random_predictions, name="Random")

    """  Dump all variables of the two confusion matrices """
    print("--------------------")
    chads_vasc_cm.dump()
    print("--------------------")
    ml_cm.dump()
    #  print("--------------------")
    #  random_cm.dump()

if __name__ == "__main__":
    main()
