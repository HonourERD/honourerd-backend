from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)


all_attributes = {
    "PATIENTID": "Patient",
    "PATIENTNAME": "Patient",
    "PATIENTEMAIL": "Patient",
    "PATIENTTEL": "Patient",
    "AGE": "Patient",
    "DOB": "Patient",
    "PATIENTADDRESS": "Patient",
    "DOCTORID": "Doctor",
    "DOCTORNAME": "Doctor",
    "DOCTORSPECIALTY": "Doctor",
    "APPOINTMENTDATE": "Appointment",
    "APPOINTMENTTIME": "Appointment",
    "DIAGNOSIS": "Diagnosis",
    "MEDICATION": "Medication"
}


def normalize_data(student_input):
   
    normalized_data = []
    for attr in student_input:
        normalized_data.append((attr, all_attributes.get(attr, "Unknown")))

    df = pd.DataFrame(normalized_data, columns=["Attribute", "Belongs To"])

  
    atomicity_fixes = {
        "PATIENTNAME": ["PATIENTFIRSTNAME", "PATIENTLASTNAME"],
        "DOCTORNAME": ["DOCTORFIRSTNAME", "DOCTORLASTNAME"]
    }
    
    expanded_data = []
    for attr, table in zip(df["Attribute"], df["Belongs To"]):
        if attr in atomicity_fixes:
            for split_attr in atomicity_fixes[attr]:
                expanded_data.append((split_attr, table))
        else:
            expanded_data.append((attr, table))

    df = pd.DataFrame(expanded_data, columns=["Attribute", "Belongs To"])

   
    partial_dependencies = {
        "AGE": "PatientDetails",
        "DOB": "PatientDetails",
        "PATIENTEMAIL": "PatientDetails",
        "PATIENTTEL": "PatientDetails"
    }

    df["Belongs To"] = df.apply(lambda row: partial_dependencies[row["Attribute"]]
                                if row["Attribute"] in partial_dependencies else row["Belongs To"], axis=1)

    
    transitive_dependencies = {
        "DOCTORSPECIALTY": "Doctor"
    }

    df["Belongs To"] = df.apply(lambda row: transitive_dependencies[row["Attribute"]]
                                if row["Attribute"] in transitive_dependencies else row["Belongs To"], axis=1)

    return df.to_dict(orient="records")  


@app.route("/normalize", methods=["POST"])
def normalize():
    data = request.json  
    student_input = data.get("attributes", [])

    if not student_input:
        return jsonify({"error": "No attributes provided!"}), 400

    normalized_data = normalize_data(student_input)
    return jsonify({"normalized_data": normalized_data})

if __name__ == "__main__":
    app.run(debug=True)
