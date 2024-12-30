from phongmachapp.models import *
from phongmachapp.utilities import *

def cashier_get_medical_examination_form(date=None):
    data = db.session.query(
        func.date(MedicalExaminationForm.appointment_date),
        MedicalExaminationForm.id,
        User.full_name,

    ) .select_from(MedicalExaminationForm)\
    .join(User,User.id == MedicalExaminationForm.patient_id)\
        .order_by(func.date(MedicalExaminationForm.appointment_date).desc(),
                  MedicalExaminationForm.id.desc()
                  )
    if date:
        data=data.filter(
            func.date(MedicalExaminationForm.appointment_date) == date
        )
    result = data.all()
    medical_examination_forms = [
        {
            "appointment_date": medical_examination_form[0],
            "id": medical_examination_form[1],
            "full_name":medical_examination_form[2],
            "payment_invoice":get_payment_by_medical_examination_form_id(medical_examination_form[1]),
        }
        for medical_examination_form in result
    ]
    return medical_examination_forms



def cashier_get_handle_payment_by_medical_examination_form_id(medical_examination_form_id=None):
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
        medicines=get_medicine_by_medical_examination_form_id(medical_examination_form_id)
        data = db.session.query(
            User.full_name,
            func.date(MedicalExaminationForm.appointment_date),
        ).select_from(MedicalExaminationForm) \
            .join(User, User.id == MedicalExaminationForm.patient_id) \
            .filter(MedicalExaminationForm.id == medical_examination_form_id) \
            .first()
        sum_medicine_price=0
        for medicine in medicines:
            sum_medicine_price+=medicine['quantity']*medicine['price']
        result = {
            'full_name': data[0],
            'appointment_date': data[1].strftime("%Y-%m-%d"),
            'medical_fee': app.config['MEDICAL_FEE'],
            'medicine_price': sum_medicine_price,
            'total_price': sum_medicine_price+ app.config['MEDICAL_FEE'],
            'is_pay': False
        }
        return result

    result = {
        'full_name': data[0],
        'appointment_date': data[1].strftime("%Y-%m-%d"),
        'medical_fee': data[2],
        'medicine_price': data[3],
        'total_price': data[3] + data[2] ,
        'is_pay':True
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
            medicine_price=medicine_price,
            cashier_id=cashier_id,
            medical_examination_form_id=medical_examination_form_id,
        )
        db.session.add(payment_invoice)
        db.session.commit()
def get_medicine_by_medical_examination_form_id(medical_examination_id=None):
    data = db.session.query(
        Medicine.name,
        Unit.name,
        MedicalExaminationFormDetail.quantity,
        MedicalExaminationFormDetail.how_to_use,

        Medicine.price,
        MedicalExaminationFormDetail.id,
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
            'price': item[4]

        }
        for item in result
    ]
    return medicine

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
        'medical_fee': data[2],
        'medicine_price': data[3],
        'total_price': data[3] + data[2]  # Sử dụng label để lấy tổng giá trị
    }

    return result
def check_user_exist(username,email):
    user_has_same_name = User.query.filter(User.username.__eq__(username.strip())).first()
    if user_has_same_name:
        return True,"Tên đăng nhập đã tồn tại"
    user_has_same_email = User.query.filter(User.email.__eq__(email.strip())).first()
    if user_has_same_email:
        return True,"Email đã tồn tại"

    return False,None

def cashier_add_new_user(username, passwd, full_name, phone_number, email,year_of_birth=None,address=None,is_male=True):
    #  neu da ton tai nguoi dung
    success,error = check_user_exist(username,email)
    if success:
        return None,False,error

    passwd = __hash_password(passwd)
    user = User(
        username=username,
        password=passwd,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        user_type=UserType.NGUOI_DUNG,
        year_of_birth=year_of_birth if year_of_birth else 2000,
        address=address if address else 'TP.Hồ Chí Minh',
        is_male=is_male,
    )
    try:
        db.session.add(user)
        db.session.commit()
        return user,True,None
    except Exception as e:
        return None,False,str(e)

def cashier_add_new_waiting_list(user_id,time_frame,appointment_date):
    waiting_entry = WaitingList(
        user_id=user_id,
        time_frame=time_frame,
        appointment_date=appointment_date
    )
    db.session.add(waiting_entry)
    db.session.commit()
def __hash_password(passwd):
    return str(hashlib.md5(passwd.encode('utf-8')).hexdigest())
if __name__ == "__main__":
    with app.app_context():
        pass
