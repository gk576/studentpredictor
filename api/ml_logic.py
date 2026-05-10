from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

TRAINING_DATA = {
    'hours': [2,10,5,1,8,3,9,4,5,6,7,8,9,10,7.5,6.5,8.5,9.5,4,5,4.5,3,5.5,6,4,3.5,5,4.5,2,1.5,2.5,1,3,2,1.5,2,3,1,4,6],
    'attendance': [40,95,70,30,85,50,90,60,70,80,85,90,95,98,82,75,88,92,60,65,62,55,68,72,58,52,66,64,38,30,45,22,50,35,28,40,48,18,65,78],
    'result': [0,1,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1]
}

def get_model_and_accuracy():
    df = pd.DataFrame(TRAINING_DATA)
    X = df[['hours', 'attendance']]
    y = df['result']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    return model, round(accuracy * 100, 1)

def predict_student_success(study_hours, attendance):
    model, accuracy = get_model_and_accuracy()
    proba = model.predict_proba([[study_hours, attendance]])[0]
    prediction = model.predict([[study_hours, attendance]])[0]
    result = "Pass" if prediction == 1 else "Fail"
    confidence = round(max(proba) * 100, 1)
    return result, confidence, accuracy
