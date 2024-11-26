from models import *
from phongmachapp import app
import hashlib

def load_user():
    return User.query.all()

def check_user(name,passwd):
    query=User.query
    passwd=str(hashlib.md5(passwd.strip().encode('utf-8')).hexdigest())
    query=query.filter(User.username.__eq__(name.strip()), User.password.__eq__(passwd)).first()
    return query
