from sklearn.tree import DecisionTreeClassifier
import pandas as pd

def predict_student_success(study_hours, attendance):
    # 1. Mock Data: Training the AI (Task 1.5)
    # 0 = Fail, 1 = Pass
    data = {
        'hours': [2, 10, 5, 1, 8, 3, 9, 4],
        'attendance': [40, 95, 70, 30, 85, 50, 90, 60],
        'result': [0, 1, 1, 0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)

    # 2. Setup the Algorithm (Task 3)
    X = df[['hours', 'attendance']] # Inputs
    y = df['result']                # Output (Label)
    
    model = DecisionTreeClassifier()
    model.fit(X, y) # This is the "Training" phase

    # 3. Make a prediction
    prediction = model.predict([[study_hours, attendance]])
    
    return "Pass" if prediction[0] == 1 else "Fail"