from phongmachapp.models import *

def get_patient_list(patient_list_id=None):
    data= db.session.query(
        func.date( PatientList.appointment_date),
        PatientList.id,
        PatientListDetail.user_id,
        User.full_name,
    ).select_from(PatientList)\
    .join(PatientListDetail,PatientListDetail.patient_list_id == PatientList.id)\
    .join(User,User.id== PatientListDetail.user_id)\
    .order_by(PatientList.id)
    return data.all()

def get_history_patient(patient_id=None):
    data= db.session.query(
        func.date( MedicalExaminationForm.appointment_date),
        User.full_name,
        MedicalExaminationForm.symptom,
        MedicalExaminationForm.predicted_disease,
    ).select_from(MedicalExaminationForm)\
    .join(User,User.id==MedicalExaminationForm.patient_id)\
    .order_by( func.date( MedicalExaminationForm.appointment_date))
    if patient_id:
        data= data.filter(MedicalExaminationForm.patient_id==patient_id)
    return data.all()