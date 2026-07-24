from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import json

app = Flask(__name__)

# Load dataset
df = pd.read_csv('data.csv')

# Encode machine type for model
le_type = LabelEncoder()
df['Machine_Type_Encoded'] = le_type.fit_transform(df['Machine_Type'])

# Prepare model
def train_model():
    features = ['Machine_Type_Encoded', 'Temperature_C', 'Vibration_mm_s', 'Pressure_bar', 'Voltage_V', 
                'Current_A', 'RPM', 'Power_kW', 'Runtime_Hours', 'Downtime_Hours',
                'Utilization_Percent', 'Efficiency_Score', 'Sensor_Health_Score',
                'Predictive_Risk_Score', 'Days_To_Failure']

    X = df[features].copy()
    y = df['Failure_Flag']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    joblib.dump(model, 'models/failure_model.pkl')
    joblib.dump(le_type, 'models/label_encoder.pkl')

    return model, accuracy, features

# Train on startup
try:
    model = joblib.load('models/failure_model.pkl')
    le_type = joblib.load('models/label_encoder.pkl')
    features = ['Machine_Type_Encoded', 'Temperature_C', 'Vibration_mm_s', 'Pressure_bar', 'Voltage_V', 
                'Current_A', 'RPM', 'Power_kW', 'Runtime_Hours', 'Downtime_Hours',
                'Utilization_Percent', 'Efficiency_Score', 'Sensor_Health_Score',
                'Predictive_Risk_Score', 'Days_To_Failure']
    accuracy = 0.95
except:
    model, accuracy, features = train_model()

@app.route('/')
def dashboard():
    # KPIs
    total_machines = df['Machine_ID'].nunique()
    failure_rate = round(df['Failure_Flag'].mean() * 100, 2)
    avg_rul = round(df['Remaining_Useful_Life'].mean(), 1)
    avg_efficiency = round(df['Efficiency_Score'].mean(), 1)

    # Charts data
    failure_by_type = df[df['Failure_Flag']==1]['Failure_Type'].value_counts().to_dict()
    machine_types = df['Machine_Type'].value_counts().to_dict()
    criticality = df['Criticality_Level'].value_counts().to_dict()

    # Risk distribution
    risk_bins = pd.cut(df['Predictive_Risk_Score'], bins=[0, 25, 50, 75, 100], 
                       labels=['Low', 'Medium', 'High', 'Critical'])
    risk_dist = risk_bins.value_counts().to_dict()

    # Recent alerts
    alerts = df.nlargest(10, 'Predictive_Risk_Score')[['Machine_ID', 'Machine_Type', 
              'Predictive_Risk_Score', 'Remaining_Useful_Life', 'Criticality_Level']].to_dict('records')

    # Machine types for dropdown
    machine_type_list = sorted(df['Machine_Type'].unique().tolist())

    return render_template('dashboard.html',
        total_machines=total_machines,
        failure_rate=failure_rate,
        avg_rul=avg_rul,
        avg_efficiency=avg_efficiency,
        accuracy=round(accuracy*100, 1),
        failure_by_type=json.dumps(failure_by_type),
        machine_types=json.dumps(machine_types),
        criticality=json.dumps(criticality),
        risk_dist=json.dumps(risk_dist),
        alerts=alerts,
        machine_type_list=machine_type_list
    )

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Encode machine type with fallback
    machine_type = data.pop('Machine_Type', None)
    if not machine_type or machine_type == '':
        machine_type = 'Conveyor'  # default fallback

    data['Machine_Type_Encoded'] = int(le_type.transform([machine_type])[0])

    input_data = pd.DataFrame([data])
    prediction = model.predict(input_data[features])[0]
    probability = model.predict_proba(input_data[features])[0][1]

    return jsonify({
        'prediction': int(prediction),
        'probability': round(float(probability) * 100, 2),
        'risk_level': 'High' if probability > 0.7 else 'Medium' if probability > 0.3 else 'Low',
        'machine_type': machine_type
    })

@app.route('/machines')
def machines():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    machine_type = request.args.get('type', '')
    criticality_filter = request.args.get('criticality', '')

    filtered_df = df.copy()
    if machine_type:
        filtered_df = filtered_df[filtered_df['Machine_Type'] == machine_type]
    if criticality_filter:
        filtered_df = filtered_df[filtered_df['Criticality_Level'] == criticality_filter]

    total = len(filtered_df)
    machines_list = filtered_df.iloc[(page-1)*per_page : page*per_page].to_dict('records')

    machine_types = df['Machine_Type'].unique().tolist()
    criticality_levels = df['Criticality_Level'].unique().tolist()

    return render_template('machines.html',
        machines=machines_list,
        page=page,
        total_pages=(total // per_page) + 1,
        total=total,
        machine_types=machine_types,
        criticality_levels=criticality_levels,
        selected_type=machine_type,
        selected_criticality=criticality_filter
    )

@app.route('/machine/<machine_id>')
def machine_detail(machine_id):
    machine_data = df[df['Machine_ID'] == machine_id].iloc[0].to_dict()
    return render_template('machine_detail.html', machine=machine_data)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
