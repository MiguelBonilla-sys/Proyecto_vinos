import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
import os
from dotenv import load_dotenv
import psycopg2

# Cargar variables de entorno y conectar a Postgres
target_line="df = pd.read_csv('vinos.csv')"
load_dotenv()
db_url = os.getenv('POSTGRES_URL').strip("'\"")
conn = psycopg2.connect(db_url)
df = pd.read_sql("SELECT * FROM vinos", conn)

df['quality'] = df['quality'].replace(['Excepcional','Excelente', 'Muy Bueno', 'Bueno', 'Regular', 'Vino defectuoso'], [5, 4, 3, 2, 1, 0])
df.value_counts('quality')

x = df.drop('quality', axis=1)
y = df['quality']

xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.2, random_state=42)

dt_Classifier = DecisionTreeClassifier()
dt_Classifier.fit(xtrain, ytrain)
y_pred = dt_Classifier.predict(xtest)
mse_dt = accuracy_score(ytest, y_pred)
print("Mean Squared Error (MSE) for Decision Tree:", mse_dt)

pickle.dump(dt_Classifier, open(r'dt_Classifier_ptap.pkl', 'wb'))

xgb_classfier = XGBClassifier()
xgb_classfier.fit(xtrain, ytrain)
y_pred = xgb_classfier.predict(xtest)
mse_xgb = accuracy_score(ytest, y_pred)
print("Mean Squared Error (MSE) for xgb_classfier:", mse_xgb)

pickle.dump(xgb_classfier, open(r'xgb_classfier_ptap.pkl', 'wb'))

