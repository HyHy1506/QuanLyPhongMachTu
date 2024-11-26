from flask import render_template, request, redirect, url_for, session
from phongmachapp import app
from dao.dao_user import add_new_user,check_user_login,get_user_by_id
import hashlib
from models import UserType,User


@app.route('/')
def index():
    # kiem tra da dang nhap chua
    if not session.get('logged_in'):
        return render_template("index.html")

    # lay ten dang nhap de hien thi
    user_id= session.get('user_id')
    user=get_user_by_id(user_id)



    return render_template("index.html",user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method.__eq__('POST'):
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = check_user_login(username, password)

        if user:
            # luu thong tin phien dang nhap
            __save_session(user)

            # kiem tra loai nguoi dung , sau do chuyen toi trang lam viec
            return __direct_correct_page(user.user_type)
        else:
            return render_template('login.html', error='Sai tài khoản hoặc mật khẩu')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method.__eq__('POST'):
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        full_name = request.form['full_name'].strip()
        phone_number = request.form['phone_number'].strip()
        email = request.form['email'].strip()
        # kiem tra ten dang nhap va email ton tai chua
        success,error = add_new_user(username, password, full_name, phone_number, email)
        if success:
            return redirect('/login')
        else:
            return render_template('signup.html', error=error)

    return render_template('signup.html')


@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    # neu phien dang nhap bi xoa
    if not session.get('logged_in'):
        return redirect('/login')

    # neu khong phai bac si ,phai dang nhap
    if session.get('user_type') != UserType.BAC_SI:
        return redirect('/login')

    # --------------------------------
    # sau khi co phien dang nhap
    user_id = session['user_id']

    # xu ly code o day












    # --------------------------------

    return render_template('doctor.html')


@app.route('/nurse', methods=['GET', 'POST'])
def nurse():
    # neu phien dang nhap bi xoa
    if not session.get('logged_in'):
        return redirect('/login')

    # neu khong phai y ta ,phai dang nhap
    if session.get('user_type') != UserType.Y_TA:
        return redirect('/login')

    # --------------------------------
    # sau khi co phien dang nhap
    user_id = session['user_id']

    # xu ly code o day













    # --------------------------------

    return render_template('nurse.html')


@app.route('/user-patient', methods=['GET', 'POST'])
def user_patient():
    # neu phien dang nhap bi xoa
    if not session.get('logged_in'):
        return redirect('/login')

    # neu khong phai benh nhan ,phai dang nhap
    if session.get('user_type') != UserType.NGUOI_DUNG:
        return redirect('/login')

    # --------------------------------
    # sau khi co phien dang nhap
    user_id = session['user_id']

    # xu ly code o day















    # --------------------

    return render_template('user.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # neu phien dang nhap bi xoa
    if not session.get('logged_in'):
        return redirect('/login')

    # neu khong phai quan tri vien ,phai dang nhap
    if session.get('user_type') != UserType.QUAN_TRI_VIEN:
        return redirect('/login')

    # --------------------------------
    # sau khi co phien dang nhap
    user_id = session['user_id']

    # xu ly code o day













    # --------------------
    return render_template('admin.html')


@app.route('/logout')
def logout():
    # xoa het phien lam viec
    __clear_session()
    return redirect('/')


# luu thong tin phien dang nhap
def __save_session(user):
    session['logged_in'] = True
    session['username'] = user.username
    session['user_id'] = user.id
    session['user_type'] = user.user_type.value


def __clear_session():
    session.clear()


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


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
