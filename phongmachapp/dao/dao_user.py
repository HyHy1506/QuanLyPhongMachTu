import hashlib
from phongmachapp.models import *

def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_user_login(name, passwd):
    query = User.query
    # giai ma mat khau tu trang login
    passwd = __hash_password(passwd)
    return query.filter(User.username.__eq__(name.strip()), User.password.__eq__(passwd)).first()


def check_user_exist(username,email):
    user_has_same_name = User.query.filter(User.username.__eq__(username.strip())).first()
    if user_has_same_name:
        return True,"Tên đăng nhập đã tồn tại"
    user_has_same_email = User.query.filter(User.email.__eq__(email.strip())).first()
    if user_has_same_email:
        return True,"Email đã tồn tại"

    return False,None


def add_new_user(username, passwd, full_name, phone_number, email):
    #  neu da ton tai nguoi dung
    success,error = check_user_exist(username,email)
    if success:
        return False,error

    passwd = __hash_password(passwd)
    user = User(
        username=username,
        password=passwd,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        user_type=UserType.NGUOI_DUNG
    )
    try:
        __add_user(user)
        return True,None
    except Exception as e:
        return False,str(e)

def update_user(user_id,avatar=None,full_name=None,username=None,phone_number=None,email=None):
    user = get_user_by_id(user_id)
    if user:
        if avatar:
            user.avatar = avatar
        if full_name:
            user.full_name = full_name
        if username:
            user.username = username
        if phone_number:
            user.phone_number = phone_number
        if email:
            user.email = email
        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()  # Quay lại nếu có lỗi
            return False, str(e)

def __add_user(user):
    db.session.add(user)
    db.session.commit()


def __hash_password(passwd):
    return str(hashlib.md5(passwd.encode('utf-8')).hexdigest())
