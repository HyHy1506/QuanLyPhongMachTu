from sqlalchemy import false
from sqlalchemy.testing.suite.test_reflection import users

from models import *
from phongmachapp import app
import hashlib


def check_user_login(name, passwd):
    query = User.query
    # giai ma mat khau tu trang login
    passwd = __hash_password(passwd)
    return query.filter(User.username.__eq__(name.strip()), User.password.__eq__(passwd)).first()


def check_user_exist(username, passwd, email):
    query = User.query
    # giai ma mat khau tu trang login
    passwd = __hash_password(passwd)
    return query.filter(User.username.__eq__(username.strip()),
                        User.password.__eq__(passwd),
                        User.email.__eq__(email)).first()


def add_new_user(username, passwd, full_name, phone_number, email):
    #  neu da ton tai nguoi dung
    if check_user_exist(username, passwd, email):
        return False

    passwd = __hash_password(passwd)
    user = User(
        username=username,
        password=passwd,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        user_type=UserType.NGUOI_DUNG
    )
    __add_user(user)
    return True


def __add_user(user):
    db.session.add(user)
    db.session.commit()


def __hash_password(passwd):
    return str(hashlib.md5(passwd.encode('utf-8')).hexdigest())
