from flask import render_template, request, redirect, url_for, session, flash
from phongmachapp import app, login
from dao.dao_user import add_new_user, check_user_login, get_user_by_id, update_user
import hashlib
from models import UserType, User
from flask_login import current_user, login_user, logout_user
import cloudinary.uploader
from datetime import datetime
from phongmachapp.dao.dao_doctor import get_patient_list, get_history_patient, get_medicine, \
    get_medical_examination_form_by_user_id, create_new_medical_examination_form, \
    get_full_medical_examination_form_by_medical_examination_form, \
    get_medicine_by_medical_examination_form_id, get_unit,\
    create_new_medical_examination_form_detail,\
    update_medical_examination_form
from phongmachapp.dao.dao_user_patient import get_history_register_examination_by_user_id, get_history_examination, \
    add_waiting_list
from phongmachapp.utilities import FunctionUserPatientEnum
from sqlalchemy import func


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login_current_user():
    if (current_user.is_authenticated):
        return redirect("/")
    if request.method.__eq__('POST'):
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = check_user_login(username, password)

        if user:
            # luu thong tin phien dang nhap
            login_user(user)
            # kiem tra loai nguoi dung , sau do chuyen toi trang lam viec
            return __direct_correct_page(user.user_type)
        else:
            return render_template('login.html', error='Sai tài khoản hoặc mật khẩu')

    return render_template('login.html')


@login.user_loader
def load_current_user(user_id):
    return get_user_by_id(user_id)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method.__eq__('POST'):
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        full_name = request.form['full_name'].strip()
        phone_number = request.form['phone_number'].strip()
        email = request.form['email'].strip()
        # kiem tra ten dang nhap va email ton tai chua
        success, error = add_new_user(username, password, full_name, phone_number, email)
        if success:
            return redirect('/login')
        else:
            return render_template('signup.html', error=error)

    return render_template('signup.html')


@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    # neu chua dang nhap
    if not current_user.is_authenticated:
        return redirect('/')

    # neu khong phai bac si
    if current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    # --------------------------------

    # xu ly code o day

    report = get_patient_list()

    # --------------------------------

    return render_template('doctor.html', report=report)


@app.route('/history_patient')
def history_patient():
    # neu chua dang nhap
    if not current_user.is_authenticated:
        return redirect('/')

    # neu khong phai bac si
    if current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    # --------------------------------

    # xu ly code o day
    patient_id = request.args.get('patient_id')
    report = get_history_patient(patient_id)

    # --------------------------------

    return render_template('doctor/history_patient.html',
                           report=report,
                           patient_id=patient_id,
                           )


@app.route('/medical_examination')
def medical_examination():
    # neu chua dang nhap
    if not current_user.is_authenticated:
        return redirect('/')

    # neu khong phai bac si
    if current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    # --------------------------------

    # xu ly code o day
    current_date = datetime.now().strftime('%d-%m-%Y')
    patient_id = request.args.get('patient_id')
    report = get_medical_examination_form_by_user_id(patient_id)
    # --------------------------------

    return render_template('doctor/medical_examination.html',
                           report=report,
                           patient_id=patient_id,
                           current_date=current_date
                           )


@app.route('/edit_medical_examination_form')
def edit_medical_examination_form():
    # neu chua dang nhap
    if not current_user.is_authenticated:
        return redirect('/')

    # neu khong phai bac si
    if current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    # --------------------------------
    # xu ly code o day
    medical_examination_form_id = request.args.get('medical_examination_form_id')
    info_medical_examination_form = get_full_medical_examination_form_by_medical_examination_form(
        medical_examination_form_id=medical_examination_form_id
    )[0]
    medicine_report = get_medicine_by_medical_examination_form_id(
        medical_examination_id=medical_examination_form_id
    )
    units = get_unit()
    medicines = get_medicine()
    # --------------------------------

    return render_template('doctor/edit_medical_examination_form.html',
                           medical_examination_form_id=medical_examination_form_id,
                           info_medical_examination_form=info_medical_examination_form,
                           medicine_report=medicine_report,
                           units=units,
                           medicines=medicines,
                           )


@app.route('/add-medical-form', methods=['POST'])
def add_medical_form():
    # Lấy dữ liệu từ form
    appointment_date = func.now()
    symptom = request.form.get('symptom')
    predicted_disease = request.form.get('predicted_disease')

    doctor_id = current_user.id  # Cần đảm bảo bạn có hệ thống đăng nhập
    patient_id = request.args.get('patient_id')  # ID bệnh nhân có thể truyền qua URL hoặc form

    create_new_medical_examination_form(
        appointment_date=appointment_date,
        symptom=symptom,
        predicted_disease=predicted_disease,
        doctor_id=doctor_id,
        patient_id=patient_id
    )
    return redirect(url_for('medical_examination', patient_id=patient_id))


@app.route('/add_medicine_to_medical_examination_form', methods=['POST'])
def add_medicine_to_medical_examination_form():
    medical_examination_form_id=request.args.get('medical_examination_form_id')

    medicine_id = request.form.get('medicine_id')
    unit_id = request.form.get('unit_id')
    quantity = request.form.get('quantity')
    how_to_use = request.form.get('how_to_use')

    create_new_medical_examination_form_detail(
        quantity=quantity,
        medicine_id=medicine_id,
        unit_id=unit_id,
        how_to_use=how_to_use,
        medical_examination_form_id=medical_examination_form_id
    )
    return redirect(url_for('edit_medical_examination_form',
                            medical_examination_form_id=medical_examination_form_id,
                           ))

@app.route('/save_medical_examination_form', methods=['POST'])
def save_medical_examination_form():
    medical_examination_form_id=request.args.get('medical_examination_form_id')

    symptom = request.form.get('symptom')
    predicted_disease = request.form.get('predicted_disease')


    result =update_medical_examination_form(
        symptom=symptom,
        predicted_disease=predicted_disease,
        medical_examination_form_id=medical_examination_form_id
    )
    return redirect(url_for('edit_medical_examination_form',
                            medical_examination_form_id=medical_examination_form_id,

                           ))

@app.route('/history_patient/add_medicine')
def add_medicine(mediciane_id=None):
    if not current_user.is_authenticated:
        return redirect('/')

        # neu khong phai bac si
    if current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    patient_id = request.args.get('id')
    report = get_medicine(mediciane_id)

    return render_template('doctor/add_medicine.html', report=report)


@app.route('/nurse', methods=['GET', 'POST'])
def nurse():
    # neu chua dang nhap
    if not current_user.is_authenticated:
        return redirect('/')

    # neu khong phai y ta
    if current_user.user_type != UserType.Y_TA:
        return redirect('/')

    # --------------------------------

    # xu ly code o day

    # --------------------------------

    return render_template('nurse.html')


@app.route('/user-patient', methods=['GET', 'POST'])
def user_patient():
    # neu chua dang nhap
    if not current_user.is_authenticated:
        return redirect('/')

    # neu khong phai nguoi dung
    if current_user.user_type != UserType.NGUOI_DUNG:
        return redirect('/')

    # --------------------------------

    # xu ly code o day
    my_func = FunctionUserPatientEnum.REGISTER_EXAMINATION
    request_func = request.args.get('func')
    try:
        # Chuyển chuỗi request_func thành Enum
        request_func_enum = FunctionUserPatientEnum(request_func)
    except ValueError:
        # Nếu không chuyển được, mặc định là REGISTER_EXAMINATION
        request_func_enum = FunctionUserPatientEnum.REGISTER_EXAMINATION

    if request_func_enum == FunctionUserPatientEnum.HISTORY_REGISTER:
        my_func = FunctionUserPatientEnum.HISTORY_REGISTER
        report_history_register = get_history_register_examination_by_user_id(user_id=current_user.id)
        return render_template('user.html',
                               current_function=my_func,
                               report_history_register=report_history_register,
                               )

    elif request_func_enum == FunctionUserPatientEnum.HISTORY_EXAMINATION:
        my_func = FunctionUserPatientEnum.HISTORY_EXAMINATION
        report_history_examination = get_history_examination(current_user.id)
        return render_template('user.html',
                               current_function=my_func,
                               report_history_examination=report_history_examination,
                               )

    elif request_func_enum == FunctionUserPatientEnum.NOTIFICATION:
        my_func = FunctionUserPatientEnum.NOTIFICATION
        return render_template('user.html', current_function=my_func)

    else:
        my_func = FunctionUserPatientEnum.REGISTER_EXAMINATION
        time_frame = 1
        appointment_date = 1
        if request.method == 'POST':
            # Lấy dữ liệu từ form
            time_frame = request.form.get('time_frame')
            appointment_date = request.form.get('appointment_date')
            # HTML date -> Python datetime
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d')

            # # Kiểm tra dữ liệu
            if not appointment_date or not time_frame:
                pass
            else:
                add_waiting_list(
                    user_id=current_user.id,
                    time_frame=time_frame,
                    appointment_date=appointment_date,
                )
                pass

        return render_template('user.html',
                               current_function=my_func,
                               time_frame=time_frame,
                               appointment_date=appointment_date
                               )

    # --------------------


@app.route('/info-user', methods=['GET', 'POST'])
def info_current_user():
    if request.method.__eq__('POST'):
        avatar = request.files['avatar']
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']
            update_user(current_user.id, avatar_path)

    return render_template("info_user.html")


# @app.route('/admin', methods=['GET', 'POST'])
# def admin():
#     # neu chua dang nhap
#     if not current_user.is_authenticated:
#         return redirect('/')
#
#     # neu khong phai quan tri vien
#     if current_user.user_type != UserType.QUAN_TRI_VIEN:
#         return redirect('/')
#
#     # --------------------------------
#
#
#     # xu ly code o day
#
#
#
#
#
#
#
#
#
#
#
#
#
#     # --------------------
#     return render_template('admin.html')
#

@app.route('/logout')
def logout():
    # xoa het phien lam viec
    logout_user()
    return redirect('/')


# kiem tra loai nguoi dung , sau do chuyen toi trang lam viec
def __direct_correct_page(user_type):
    if user_type == UserType.BAC_SI:
        return redirect('/doctor')
    if user_type == UserType.Y_TA:
        return redirect('/nurse')
    if user_type == UserType.NGUOI_DUNG:
        return redirect('/user-patient')
    if user_type == UserType.QUAN_TRI_VIEN:
        return redirect('/admin')
    else:
        return redirect('/')


@app.context_processor
def common_attributes():
    return {
        'FunctionUserPatientEnum': FunctionUserPatientEnum
    }


if __name__ == '__main__':
    with app.app_context():
        from phongmachapp import admin

        app.run(debug=True)
