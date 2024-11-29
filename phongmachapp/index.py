from flask import render_template, request, redirect, url_for, session
from phongmachapp import app,login
from dao.dao_user import add_new_user,check_user_login,get_user_by_id,update_user
import hashlib
from models import UserType,User
from flask_login import current_user,login_user,logout_user
import cloudinary.uploader

@app.route('/')
def index():




    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login_current_user():
    if(current_user.is_authenticated):
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
        success,error = add_new_user(username, password, full_name, phone_number, email)
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












    # --------------------------------

    return render_template('doctor.html')


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















    # --------------------

    return render_template('user.html')

@app.route('/info-user', methods=['GET', 'POST'])
def info_current_user():

    if request.method.__eq__('POST'):
        avatar = request.files['avatar']
        if avatar:
            res =cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']
            update_user(current_user.id, avatar_path)

    return render_template("info_user.html")
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # neu chua dang nhap
    if not current_user.is_authenticated:
        return redirect('/')

    # neu khong phai quan tri vien
    if current_user.user_type != UserType.QUAN_TRI_VIEN:
        return redirect('/')

    # --------------------------------


    # xu ly code o day













    # --------------------
    return render_template('admin.html')


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


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
