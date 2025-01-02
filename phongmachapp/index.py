from flask import render_template, request, redirect, url_for, session, flash, jsonify
from phongmachapp import app, login
from phongmachapp.dao.dao_user import add_new_user, check_user_login, get_user_by_id, update_user
from phongmachapp import admin
import hashlib
from phongmachapp.models import UserType, User
from flask_login import current_user, login_user, logout_user
import cloudinary.uploader
from datetime import datetime
from phongmachapp.dao.dao_doctor import get_patient_list, get_history_patient, get_medicine, \
    get_medical_examination_form_by_user_id, create_new_medical_examination_form, \
    get_full_medical_examination_form_by_medical_examination_form, \
    get_medicine_by_medical_examination_form_id, get_unit, \
    create_new_medical_examination_form_detail, \
    update_medical_examination_form, get_payment_by_medical_examination_form_id, \
    create_payment_invoice
from phongmachapp.dao.dao_user_patient import get_history_register_examination_by_user_id, get_history_examination, \
    add_waiting_list,get_notification
from phongmachapp.dao.dao_yta import get_waiting_user_lastest, get_waiting_user_oldest, get_patient_list_last_id, \
    add_patient_list, add_patient_list_detail
from phongmachapp.dao.dao_cashier import cashier_add_new_user,cashier_add_new_waiting_list,cashier_get_medical_examination_form,cashier_get_handle_payment_by_medical_examination_form_id
from phongmachapp.utilities import FunctionUserPatientEnum
from sqlalchemy import func
from phongmachapp.utilities import *
import math

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login_current_user():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method.__eq__('POST'):
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = check_user_login(username, password)

        if user:
            login_user(user)
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
        success, error = add_new_user(username, password, full_name, phone_number, email)
        if success:
            return redirect('/login')
        else:
            return render_template('signup.html', error=error)

    return render_template('signup.html')

@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    if not current_user.is_authenticated or current_user.user_type != UserType.BAC_SI:
        return redirect('/')
    page = request.args.get("page", 1, type=int)
    date = request.args.get("date")
    if not date:
        date = datetime(2024, 11, 10)
    report, total = get_patient_list(date=date)
    pages = math.ceil(total / app.config['PAGE_SIZE'])

    return render_template('doctor.html',
                           date=date,
                           report=report,
                           pages=pages,
                           current_page=page)


@app.route('/pick_date_patient_list',  methods=['POST'])
def pick_date_patient_list():
    if not current_user.is_authenticated or current_user.user_type != UserType.BAC_SI:
        return redirect('/')
    date= request.form.get('appointment_date')
    appointment_date = datetime.strptime(date, '%Y-%m-%d')
    report, total = get_patient_list( date=appointment_date)


    return redirect(url_for('doctor',
                            date=date,

                            ))
@app.route('/history_patient')
def history_patient():
    if not current_user.is_authenticated or current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    page = request.args.get("page", 1, type=int)
    patient_id = request.args.get('patient_id')
    report, total = get_history_patient(
        patient_id=patient_id,
        page=page
    )
    pages = math.ceil(total / app.config['PAGE_SIZE'])

    return render_template('doctor/history_patient.html',
                           report=report,
                           patient_id=patient_id,
                           pages=pages,
                           current_page=page)

@app.route('/medical_examination')
def medical_examination():
    if not current_user.is_authenticated or current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    page = request.args.get("page", 1, type=int)
    current_date = datetime.now().strftime('%d-%m-%Y')
    patient_id = request.args.get('patient_id')
    report, total = get_medical_examination_form_by_user_id(
        user_id=patient_id,
        page=page
    )
    pages = math.ceil(total / app.config['PAGE_SIZE'])

    return render_template('doctor/medical_examination.html',
                           report=report,
                           patient_id=patient_id,
                           current_date=current_date,
                           pages=pages,
                           current_page=page)

@app.route('/edit_medical_examination_form')
def edit_medical_examination_form():
    if not current_user.is_authenticated or current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    medical_examination_form_id = request.args.get('medical_examination_form_id')
    info_medical_examination_form = get_full_medical_examination_form_by_medical_examination_form(
        medical_examination_form_id=medical_examination_form_id
    )[0]
    medicine_report = get_medicine_by_medical_examination_form_id(
        medical_examination_id=medical_examination_form_id
    )
    payment_invoice = get_payment_by_medical_examination_form_id(medical_examination_form_id)
    can_export_payment = False if payment_invoice else True
    units = get_unit()
    medicines = get_medicine()

    return render_template('doctor/edit_medical_examination_form.html',
                           medical_examination_form_id=medical_examination_form_id,
                           info_medical_examination_form=info_medical_examination_form,
                           medicine_report=medicine_report,
                           units=units,
                           medicines=medicines,
                           can_export_payment=can_export_payment,
                           payment_invoice=payment_invoice,
                           medical_fee=format_number(app.config['MEDICAL_FEE']))

@app.route('/add-medical-form', methods=['POST'])
def add_medical_form():
    appointment_date = func.now()
    symptom = request.form.get('symptom')
    predicted_disease = request.form.get('predicted_disease')

    doctor_id = current_user.id
    patient_id = request.args.get('patient_id')

    create_new_medical_examination_form(
        appointment_date=appointment_date,
        symptom=symptom,
        predicted_disease=predicted_disease,
        doctor_id=doctor_id,
        patient_id=patient_id
    )
    return redirect(url_for('medical_examination', patient_id=patient_id))

@app.route('/create_payment_invoice', methods=['POST'])
def create_payment_invoice_route():
    medical_fee = request.form.get('pay_medical_fee').replace(',', '')
    medicine_price = request.form.get('pay_medicine_price').replace(',', '')
    cashier_id = current_user.id
    medical_examination_form_id = request.args.get('medical_examination_form_id')

    create_payment_invoice(
        medical_fee=float(medical_fee),
        medicine_price=float(medicine_price),
        cashier_id=cashier_id,
        medical_examination_form_id=medical_examination_form_id,
    )

    return redirect(url_for('edit_medical_examination_form', medical_examination_form_id=medical_examination_form_id))

@app.route('/add_medicine_to_medical_examination_form', methods=['POST'])
def add_medicine_to_medical_examination_form():
    medical_examination_form_id = request.args.get('medical_examination_form_id')

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
                            medical_examination_form_id=medical_examination_form_id))

@app.route('/save_medical_examination_form', methods=['POST'])
def save_medical_examination_form():
    medical_examination_form_id = request.args.get('medical_examination_form_id')

    symptom = request.form.get('symptom')
    predicted_disease = request.form.get('predicted_disease')

    update_medical_examination_form(
        symptom=symptom,
        predicted_disease=predicted_disease,
        medical_examination_form_id=medical_examination_form_id
    )
    return redirect(url_for('edit_medical_examination_form',
                            medical_examination_form_id=medical_examination_form_id))

@app.route('/history_patient/add_medicine')
def add_medicine(mediciane_id=None):
    if not current_user.is_authenticated or current_user.user_type != UserType.BAC_SI:
        return redirect('/')

    patient_id = request.args.get('id')
    report, total = get_medicine(
        mediciane_id=mediciane_id,
    )

    return render_template('doctor/add_medicine.html',
                           report=report)

@app.route('/nurse', methods=['GET', 'POST'])
def nurse():
    if not current_user.is_authenticated or current_user.user_type != UserType.Y_TA:
        return redirect('/')

    option = request.args.get('option')

    if option == 'oldest':
        waiting_list = get_waiting_user_oldest()
    elif option == 'lastest':
        waiting_list = get_waiting_user_lastest()
    else:
        waiting_list = get_waiting_user_lastest()

    if request.method == 'POST':
        appointment_date = request.form.get('appointment_date')
        user_ids = request.form.get('user_ids', '').split(',')

        if not appointment_date or not user_ids:
            return jsonify({'success': False, 'message': 'Missing required data.'})
        add_patient_list(appointment_date, current_user.id)
        last_patient_list_id = get_patient_list_last_id()
        for user_id in user_ids:
            add_patient_list_detail(last_patient_list_id, user_id)

        return jsonify({'success': True, 'message': 'Patient list created successfully!'})

    return render_template('nurse.html',
                           waiting_list=waiting_list,
                           user_id=current_user.id)

@app.route('/user-patient', methods=['GET', 'POST'])
def user_patient():
    if not current_user.is_authenticated or current_user.user_type != UserType.NGUOI_DUNG:
        return redirect('/')

    page = request.args.get("page", 1, type=int)
    my_func = FunctionUserPatientEnum.REGISTER_EXAMINATION
    request_func = request.args.get('func')
    try:
        request_func_enum = FunctionUserPatientEnum(request_func)
    except ValueError:
        request_func_enum = FunctionUserPatientEnum.REGISTER_EXAMINATION

    if request_func_enum == FunctionUserPatientEnum.HISTORY_REGISTER:
        my_func = FunctionUserPatientEnum.HISTORY_REGISTER
        report_history_register, total = get_history_register_examination_by_user_id(user_id=current_user.id,
                                                                                     page=page)
        pages = math.ceil(total / app.config['PAGE_SIZE'])
        return render_template('user.html',
                               current_function=my_func,
                               report_history_register=report_history_register,
                               pages=pages,
                               current_page=page)

    elif request_func_enum == FunctionUserPatientEnum.HISTORY_EXAMINATION:
        my_func = FunctionUserPatientEnum.HISTORY_EXAMINATION
        report_history_examination, total = get_history_examination(user_id=current_user.id,
                                                                    page=page)
        pages = math.ceil(total / app.config['PAGE_SIZE'])
        return render_template('user.html',
                               current_function=my_func,
                               report_history_examination=report_history_examination,
                               pages=pages,
                               current_page=page)

    elif request_func_enum == FunctionUserPatientEnum.NOTIFICATION:
        my_func = FunctionUserPatientEnum.NOTIFICATION
        notifications,total=get_notification(current_user.id,page)
        pages = math.ceil(total / app.config['PAGE_SIZE'])

        return render_template('user.html',
                               current_function=my_func,
                               pages=pages,
                               current_page=page,
                               notifications=notifications
                               )

    else:
        my_func = FunctionUserPatientEnum.REGISTER_EXAMINATION
        time_frame = 1
        appointment_date = 1
        if request.method == 'POST':
            time_frame = request.form.get('time_frame')
            appointment_date = request.form.get('appointment_date')
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d')

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
                               appointment_date=appointment_date)

@app.route('/info-user', methods=['GET', 'POST'])
def info_current_user():
    if request.method.__eq__('POST'):
        avatar = request.files['avatar']
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']
            update_user(user_id=current_user.id,
                        avatar=avatar_path,
                        username=username,
                        full_name=full_name,
                        phone_number=phone_number,
                        email=email)

    return render_template("info_user.html")
@app.route('/cashier', methods=['GET', 'POST'])
def cashier():
    if not current_user.is_authenticated or current_user.user_type != UserType.THU_NGAN:
        return redirect('/')


    return redirect(url_for('cashier_handle_payment_invoice'))

@app.route('/cashier_handle_payment_invoice', methods=['GET', 'POST'])
def cashier_handle_payment_invoice():
    if not current_user.is_authenticated or current_user.user_type != UserType.THU_NGAN:
        return redirect('/')
    date = request.args.get('date')
    if not date:
        date=datetime(2024,12,10)
    report= cashier_get_medical_examination_form(date)

    return render_template('cashier/handle_payment_invoice.html',
                           report=report,
                           date=date,
                           )
@app.route('/pick_date_cashier_handle_payment_invoice',  methods=['POST'])
def pick_date_cashier_handle_payment_invoice():
    if not current_user.is_authenticated or current_user.user_type != UserType.THU_NGAN:
        return redirect('/')
    date= request.form.get('appointment_date')


    return redirect(url_for('cashier_handle_payment_invoice',
                            date=date,
                            ))

@app.route("/api/get_handle_payment", methods=["post"])
def api_get_handle_payment():
    mef_id=request.json.get("id")
    payment=cashier_get_handle_payment_by_medical_examination_form_id(mef_id)
    return jsonify(payment)


@app.route("/api/cashier_create_payment_invoice", methods=['POST'])
def cashier_create_payment_invoice_route():
    try:
        medical_fee = request.json.get('pay_medical_fee')
        medicine_price = request.json.get('pay_medicine_price')
        cashier_id = current_user.id
        medical_examination_form_id = request.json.get('medical_examination_form_id')

        # print(str(medical_fee) + " " + str(medicine_price) + " " + str(cashier_id) + " " + str(
        #     medical_examination_form_id))
        print(float(medical_fee))
        print(float(medicine_price))
        print(cashier_id)
        print(medical_examination_form_id)

        create_payment_invoice(
            medical_fee=float(medical_fee),
            medicine_price=float(medicine_price),
            cashier_id=cashier_id,
            medical_examination_form_id=medical_examination_form_id,
        )
        return jsonify({'status': 200})

    except Exception as e:
        print(f"Error: {str(e)}")  # Thêm log để debug
        return jsonify({'status': 500, 'error': str(e)})


@app.route('/nurse_add_new_user_to_waiting_list', methods=['GET', 'POST'])
def cashier_add_new_user_to_waiting_list():
    if not current_user.is_authenticated or current_user.user_type != UserType.Y_TA:
        return redirect('/')


    return render_template('nurse/add_new_user_to_waiting_list.html')





@app.route('/api/add_new_user_to_waiting_list', methods=['POST'])
def api_add_new_user_to_waiting_list():
    # Kiểm tra quyền truy cập
    if not current_user.is_authenticated or current_user.user_type != UserType.Y_TA:
        return jsonify({"status": 403, "message": "Không có quyền truy cập."}), 403

    # Lấy dữ liệu từ request
    data = request.get_json()
    if not data:
        return jsonify({"status": 400, "message": "Dữ liệu không hợp lệ."}), 400

    try:
        # Trích xuất dữ liệu từ JSON
        username = data.get("username")
        password = data.get("password")
        full_name = data.get("full_name")
        phone_number = data.get("phone_number")
        email = data.get("email")
        year_of_birth = data.get("year_of_birth")
        address = data.get("address")
        is_male = data.get("is_male")
        time_frame = data.get("time_frame")
        appointment_date = data.get("appointment_date")

        # Kiểm tra các trường bắt buộc
        if not all([username, password, full_name, phone_number, email, year_of_birth, address, time_frame, appointment_date]):
            return jsonify({"status": 400, "message": "Thiếu thông tin cần thiết."}), 400

        # Kiểm tra username và email trùng lặp
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({"status": 400, "message": "Tên đăng nhập hoặc email đã tồn tại."}), 400

        # Chuyển đổi ngày
        try:
            appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"status": 400, "message": "Ngày khám không hợp lệ."}), 400

        # Tạo người dùng mới
        user,success,error = cashier_add_new_user(
            username=username,
            passwd=password,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            address=address,
            year_of_birth=year_of_birth,
            is_male=is_male if is_male ==1 else False
        )
        if user:
            cashier_add_new_waiting_list(user_id=user.id,time_frame=time_frame,appointment_date=appointment_date)
        return jsonify({"status": 200, "message": "Đăng ký thành công!", "user_id": user.id}), 200


    except Exception as e:
        return jsonify({"status": 500, "message": f"Lỗi máy chủ: {str(e)}"}), 500


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

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


        app.run(debug=True)
