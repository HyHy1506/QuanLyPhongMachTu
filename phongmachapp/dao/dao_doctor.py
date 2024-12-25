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

def get_medicine(mediciane_id=None):
    data = db.session.query(
        Medicine.id,
        Medicine.name,
        Medicine.price,
        Medicine.inventory_quantity,
    )
    if mediciane_id:
        data = data.filter(Medicine.mediciane_id == mediciane_id)
    return data.all()

def get_medical_examination_form_by_user_id(user_id=None):
    data= db.session.query(
        func.date( MedicalExaminationForm.appointment_date),
        MedicalExaminationForm.id,
        MedicalExaminationForm.predicted_disease,

    )\
    .order_by(func.date(MedicalExaminationForm.appointment_date).desc(),
                        MedicalExaminationForm.id.desc()
                        )

    if user_id:
        data =data.filter(
            MedicalExaminationForm.patient_id==user_id
        )

    return data.all()

def create_new_medical_examination_form(appointment_date,symptom,predicted_disease,doctor_id,patient_id):
    # Tạo mới một bản ghi
    new_form = MedicalExaminationForm(
        appointment_date=appointment_date,
        symptom=symptom,
        predicted_disease=predicted_disease,
        doctor_id=doctor_id,
        patient_id=patient_id
    )

    # Lưu vào database
    db.session.add(new_form)
    db.session.commit()

def get_full_medical_examination_form_by_medical_examination_form(medical_examination_form_id=None):
    data= db.session.query(
        User.full_name,
        func.date(MedicalExaminationForm.appointment_date),
        MedicalExaminationForm.symptom,
        MedicalExaminationForm.predicted_disease,

    ).select_from(MedicalExaminationForm)\
        .join(User,User.id==MedicalExaminationForm.patient_id)
    if medical_examination_form_id:
        data=data.filter(
            MedicalExaminationForm.id==medical_examination_form_id
        )
    result = data.all()
    medical_examination_form = [
        {
            "full_name": item[0],
            'appointment_date': item[1],
            'symptom': item[2],
            'predicted_disease': item[3]

        }
        for item in result
    ]
    return medical_examination_form

def get_medicine_by_medical_examination_form_id(medical_examination_id=None):
    data=db.session.query(
        Medicine.name,
        Unit.name,
        MedicalExaminationFormDetail.quantity,
        MedicalExaminationFormDetail.how_to_use,
        MedicalExaminationFormDetail.id,

    ).select_from(MedicalExaminationFormDetail)\
    .join(Medicine,Medicine.id==MedicalExaminationFormDetail.medicine_id)\
    .join(Unit,Unit.id== MedicalExaminationFormDetail.unit_id)\
    .order_by(
        MedicalExaminationFormDetail.id.desc()
    )
    if medical_examination_id:
        data=data.filter(
            MedicalExaminationFormDetail.medical_examination_form_id==medical_examination_id
        )


    result = data.all()
    medicine = [
        {
            "medicine_name": item[0],
            'unit_name': item[1],
            'quantity': item[2],
            'how_to_use': item[3],


        }
        for item in result
    ]
    return medicine

def get_unit(unit_id=None):
    data=db.session.query(
        Unit.id,
        Unit.name
    ).select_from(Unit)
    if unit_id:
        data=data.filter(
            Unit.id==unit_id
        )
    result= data.all()
    units = [
        {
            "id":unit[0],
            "name":unit[1],
        }
        for unit in result
    ]
    return  units

def create_new_medical_examination_form_detail(
        quantity=None,
        unit_id=None,
        how_to_use=None,
        medical_examination_form_id=None,
        medicine_id=None,
):
    if quantity and unit_id and how_to_use and medicine_id and medical_examination_form_id:
        medical_examination_form_detail= MedicalExaminationFormDetail(
            quantity=quantity,
            unit_id=unit_id,
            how_to_use=how_to_use,
            medical_examination_form_id=medical_examination_form_id,
            medicine_id=medicine_id,
        )
        db.session.add(medical_examination_form_detail)
        db.session.commit()


from phongmachapp import db
from phongmachapp.models import MedicalExaminationForm  # Đảm bảo bạn đã import mô hình


def update_medical_examination_form(
        symptom=None,
        predicted_disease=None,
        medical_examination_form_id=None,
):
    if medical_examination_form_id:
        # Tìm bản ghi MedicalExaminationForm dựa trên medical_examination_form_id
        medical_form = db.session.query(MedicalExaminationForm).filter_by(id=medical_examination_form_id).first()

        if medical_form:
            # Cập nhật các thuộc tính nếu chúng được cung cấp
            if symptom is not None:
                medical_form.symptom = symptom
            if predicted_disease is not None:
                medical_form.predicted_disease = predicted_disease

            # Lưu thay đổi vào cơ sở dữ liệu
            db.session.commit()
            return True  # Trả về True nếu cập nhật thành công
        else:
            return False  # Trả về False nếu không tìm thấy bản ghi
    return False  # Trả về False nếu không có medical_examination_form_id