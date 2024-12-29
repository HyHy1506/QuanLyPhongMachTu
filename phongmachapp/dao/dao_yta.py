from sqlalchemy.sql.operators import truediv

from phongmachapp.models import *
from sqlalchemy import func


def get_waiting_user_oldest(user_id=None):
    data = db.session.query(
        func.date(WaitingList.appointment_date),
        User.full_name,
        User.phone_number,
        User.email,
        User.id
    ).select_from(WaitingList) \
        .join(User, WaitingList.user_id == User.id) \
        .order_by(func.date(WaitingList.appointment_date).asc())
    if user_id:
        data = data.filter(WaitingList.user_id == user_id)

    # Lấy tất cả dữ liệu
    result = data.all()

    # Chuyển đổi time_frame sang chuỗi
    infowaiting = [
        {
            "stt": idx + 1,  # Số thứ tự bắt đầu từ 1
            "user_id": item[4],
            "full_name": item[1],
            "appointment_date": item[0],
            "phone": item[2],
            "email": item[3],
        }
        for idx, item in enumerate(result)
    ]
    return infowaiting


def get_waiting_user_lastest(user_id=None):
    data = db.session.query(
        func.date(WaitingList.appointment_date),
        User.full_name,
        User.phone_number,
        User.email,
        User.id
    ).select_from(WaitingList) \
        .join(User, WaitingList.user_id == User.id) \
        .order_by(func.date(WaitingList.appointment_date).desc())
    if user_id:
        data = data.filter(WaitingList.user_id == user_id)

    # Lấy tất cả dữ liệu
    result = data.all()

    # Chuyển đổi time_frame sang chuỗi
    infowaiting = [
        {
            "stt": idx + 1,  # Số thứ tự bắt đầu từ 1
            "user_id": item[4],
            "full_name": item[1],
            "appointment_date": item[0],
            "phone": item[2],
            "email": item[3],
        }
        for idx, item in enumerate(result)
    ]
    return infowaiting


def get_patient_list_last_id():
    # Truy vấn id của bản ghi cuối cùng trong bảng PatientList
    last_patient = db.session.query(PatientList.id).order_by(PatientList.id.desc()).first()

    # Nếu bảng không có dữ liệu, trả về None
    if last_patient is None:
        return None

    return last_patient.id


def get_patient_list_last_appointment_date():
    last_patient = db.session.query(PatientList.id).order_by(PatientList.id.desc()).first()

    # Nếu bảng không có dữ liệu, trả về None
    if last_patient is None:
        return None

    return last_patient.appointment_date


def add_patient_list_detail(patient_list_id, user_id):
    if patient_list_id and user_id:
        record = PatientListDetail(
            patient_list_id=patient_list_id,
            user_id=user_id
        )
        db.session.add(record)
        db.session.commit()


def add_patient_list(appointment_date, nurse_id):
    if appointment_date and nurse_id:
        record = PatientList(
            appointment_date=appointment_date,
            nurse_id=nurse_id,
        )
        db.session.add(record)
        db.session.commit()


def get_patient_list_detail_with_id(last_patient_id, last_appointment_date):
    data = db.session.query(
        last_appointment_date,
        PatientListDetail.user_id,
    ).select_from(PatientListDetail)
    if last_patient_id:
        data = data.filter(PatientListDetail.patient_list_id == last_patient_id)
        # Lấy tất cả dữ liệu
    result = data.all()

    # Chuyển đổi sang chuỗi
    infowaiting = [
        {
            "id": item[1],
            "appointment_date": item[0],
        }
        for idx, item in enumerate(result)
    ]
    return infowaiting