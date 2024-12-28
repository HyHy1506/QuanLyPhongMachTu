from phongmachapp.models import *
def get_history_register_examination_by_user_id(user_id=None, page=None):
    data=db.session.query(
        func.date( WaitingList.appointment_date),
        WaitingList.time_frame,
    ).select_from(WaitingList)\
    .join(User,WaitingList.user_id==User.id)\
    .order_by(func.date( WaitingList.appointment_date).desc())
    if user_id:
        data=data.filter(WaitingList.user_id==user_id)

    total = data.count()
    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * page_size
        data = data.slice(start, start + page_size)

    result = data.all()

    history = [
        {
            "appointment_date": item[0],
            "time_frame": from_time_frame_to_string(item[1])
        }
        for item in result
    ]
    return history,total

def get_history_examination(user_id=None,page=None):
    data=db.session.query(
        func.date( MedicalExaminationForm.appointment_date),
        MedicalExaminationForm.predicted_disease,
        MedicalExaminationForm.symptom,
        MedicalExaminationForm.id,
    ).select_from(MedicalExaminationForm)\
    .order_by( func.date( MedicalExaminationForm.appointment_date).desc())
    if user_id:
        data=data.filter(MedicalExaminationForm.patient_id==user_id)

    total = data.count()
    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * page_size
        data = data.slice(start, start + page_size)

    result = data.all()
    history = [
        {
            "appointment_date": item[0],
            'predicted_disease':item[1],
            'symptom':item[2],
            'medicines':get_medicine_by_medical_examination_form_id(item[3])

        }
        for item in result
    ]
    return history,total

def get_medicine_by_medical_examination_form_id(medical_examination_id=None):
    data=db.session.query(
        Medicine.name,
        MedicalExaminationFormDetail.quantity,
    ).select_from(MedicalExaminationFormDetail)\
    .join(Medicine,Medicine.id==MedicalExaminationFormDetail.medicine_id)
    if medical_examination_id:
        data=data.filter(MedicalExaminationFormDetail.medical_examination_form_id==medical_examination_id)


    result = data.all()
    # Tạo chuỗi duy nhất từ các phần tử
    medicines = [
        f"&{item[0]}&+&{item[1]}&#"  # Sử dụng f-string để định dạng chuỗi
        for item in result
    ]

    # Nối tất cả các chuỗi lại với nhau
    return ''.join(medicines)  # Trả về chuỗi đã nối

def add_waiting_list(user_id=None,time_frame=None,appointment_date=None):
    if time_frame and appointment_date and user_id:
        waiting_list=WaitingList(
            user_id=user_id,
            time_frame=time_frame,
            appointment_date=appointment_date

        )
        db.session.add(waiting_list)
        db.session.commit()


def from_int_to_time_frame(time_frame_int):
    if time_frame_int:
        if time_frame_int == 0:
            return TimeFrame.SANG
        elif time_frame_int == 1:
            return TimeFrame.CHIEU
        else:
            return TimeFrame.TOI
def from_time_frame_to_string(time_frame=TimeFrame):
    if time_frame == TimeFrame.SANG:
        return 'Sáng'
    elif time_frame == TimeFrame.CHIEU:
        return 'Chiều'
    else:
        return 'Tối'