from phongmachapp.models import *
from phongmachapp.utilities import *


def get_patient_list(patient_list_id=None,page=None):
    data = db.session.query(
        func.date(PatientList.appointment_date),
        PatientList.id,
        PatientListDetail.user_id,
        User.full_name,
    ).select_from(PatientList) \
        .join(PatientListDetail, PatientListDetail.patient_list_id == PatientList.id) \
        .join(User, User.id == PatientListDetail.user_id) \
        .order_by(PatientList.id)

    total = data.count()
    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * page_size
        data = data.slice(start, start + page_size)
    return data.all(),total


def get_history_patient(patient_id=None,page =None):
    data = db.session.query(
        func.date(MedicalExaminationForm.appointment_date),
        User.full_name,
        MedicalExaminationForm.symptom,
        MedicalExaminationForm.predicted_disease,
    ).select_from(MedicalExaminationForm) \
        .join(User, User.id == MedicalExaminationForm.patient_id) \
        .order_by(func.date(MedicalExaminationForm.appointment_date))
    if patient_id:
        data = data.filter(MedicalExaminationForm.patient_id == patient_id)
    total = data.count()
    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * page_size
        data = data.slice(start, start + page_size)
    return data.all(),total


def get_medicine(mediciane_id=None,page=None):
    data = db.session.query(
        Medicine.id,
        Medicine.name,
        Medicine.price,
        Medicine.inventory_quantity,
    )
    if mediciane_id:
        data = data.filter(Medicine.mediciane_id == mediciane_id)
    return data.all()


def get_medical_examination_form_by_user_id(user_id=None,page=None):
    data = db.session.query(
        func.date(MedicalExaminationForm.appointment_date),
        MedicalExaminationForm.id,
        MedicalExaminationForm.predicted_disease,

    ) \
        .order_by(func.date(MedicalExaminationForm.appointment_date).desc(),
                  MedicalExaminationForm.id.desc()
                  )

    if user_id:
        data = data.filter(
            MedicalExaminationForm.patient_id == user_id
        )

    total = data.count()
    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * page_size
        data = data.slice(start, start + page_size)
    return data.all(),total


def create_new_medical_examination_form(appointment_date, symptom, predicted_disease, doctor_id, patient_id):
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
    data = db.session.query(
        User.full_name,
        func.date(MedicalExaminationForm.appointment_date),
        MedicalExaminationForm.symptom,
        MedicalExaminationForm.predicted_disease,

    ).select_from(MedicalExaminationForm) \
        .join(User, User.id == MedicalExaminationForm.patient_id)
    if medical_examination_form_id:
        data = data.filter(
            MedicalExaminationForm.id == medical_examination_form_id
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
    data = db.session.query(
        Medicine.name,
        Unit.name,
        MedicalExaminationFormDetail.quantity,
        MedicalExaminationFormDetail.how_to_use,
        MedicalExaminationFormDetail.id,
        Medicine.price,
    ).select_from(MedicalExaminationFormDetail) \
        .join(Medicine, Medicine.id == MedicalExaminationFormDetail.medicine_id) \
        .join(Unit, Unit.id == MedicalExaminationFormDetail.unit_id) \
        .order_by(
        MedicalExaminationFormDetail.id.desc()
    )
    if medical_examination_id:
        data = data.filter(
            MedicalExaminationFormDetail.medical_examination_form_id == medical_examination_id
        )

    result = data.all()
    medicine = [
        {
            "medicine_name": item[0],
            'unit_name': item[1],
            'quantity': item[2],
            'how_to_use': item[3],
            'price': format_number(item[4])

        }
        for item in result
    ]
    return medicine


def get_unit(unit_id=None):
    data = db.session.query(
        Unit.id,
        Unit.name
    ).select_from(Unit)
    if unit_id:
        data = data.filter(
            Unit.id == unit_id
        )
    result = data.all()
    units = [
        {
            "id": unit[0],
            "name": unit[1],
        }
        for unit in result
    ]
    return units


def create_new_medical_examination_form_detail(
        quantity=None,
        unit_id=None,
        how_to_use=None,
        medical_examination_form_id=None,
        medicine_id=None,
):
    if quantity and unit_id and how_to_use and medicine_id and medical_examination_form_id:
        medical_examination_form_detail = MedicalExaminationFormDetail(
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


def get_payment_by_medical_examination_form_id(medical_examination_form_id=None):
    if medical_examination_form_id is None:
        return None

    data = db.session.query(
        User.full_name,
        func.date(MedicalExaminationForm.appointment_date),
        PaymentInvoice.medical_fee,
        PaymentInvoice.medicine_price,

    ).select_from(PaymentInvoice) \
        .join(MedicalExaminationForm, MedicalExaminationForm.id == PaymentInvoice.medical_examination_form_id) \
        .join(User, User.id == MedicalExaminationForm.patient_id) \
        .filter(PaymentInvoice.medical_examination_form_id == medical_examination_form_id) \
        .first()

    if data is None:
        return None  # Hoặc xử lý trường hợp không có dữ liệu

    result = {
        'full_name': data[0],
        'appointment_date': data[1],
        'medical_fee': format_number(data[2]),
        'medicine_price': format_number(data[3]),
        'total_price': format_number(data[3] + data[2])  # Sử dụng label để lấy tổng giá trị
    }

    return result


def create_payment_invoice(
        medical_fee=None,
        medicine_price=None,
        cashier_id=None,
        medical_examination_form_id=None,
):
    if medical_fee and medicine_price and cashier_id and medical_examination_form_id:
        payment_invoice = PaymentInvoice(

            medical_fee=medical_fee,
            medicine_price =medicine_price,
            cashier_id =cashier_id,
            medical_examination_form_id =medical_examination_form_id,
        )
        db.session.add(payment_invoice)
        db.session.commit()
