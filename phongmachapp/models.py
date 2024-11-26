import enum
import hashlib
from sqlalchemy import Column,Integer,String,Float,ForeignKey,Enum
from sqlalchemy.orm import relationship
from phongmachapp import app,db

class UserType(str,enum.Enum):
    NGUOI_DUNG="nguoi dung"
    BAC_SI="bac si"
    Y_TA="y ta"
    QUAN_TRI_VIEN="quan tri vien"


class User(db.Model):
    id = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String(50),nullable=False,unique=True)
    password = Column(String(50),nullable=False)
    full_name = Column(String(255),nullable=False)
    phone_number = Column(String(50),nullable=False)
    email = Column(String(100),nullable=False,unique=True)
    user_type = Column(Enum(UserType),nullable=False)

if __name__ == '__main__':
    with app.app_context():
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        # db.create_all()
        # user1 = User(
        #     username="admin",
        #     password=password,
        #     full_name="Nguyen Van A",
        #     phone_number="0123456789",
        #     email="admin@gmail.com",
        #     user_type=UserType.QUAN_TRI_VIEN
        # )
        # user2 = User(
        #     username="bacsi",
        #     password=password,
        #     full_name="Nguyen Van B",
        #     phone_number="0123456789",
        #     email="doctor@gmail.com",
        #     user_type=UserType.BAC_SI
        # )
        # user3 = User(
        #     username="yta",
        #     password=password,
        #     full_name="Nguyen Van C",
        #     phone_number="0123456789",
        #     email="nurse@gmail.com",
        #     user_type=UserType.Y_TA
        # )
        # user4 = User(
        #     username="benhnhan",
        #     password=password,
        #     full_name="Nguyen Van D",
        #     phone_number="0123456789",
        #     email="patient@gmail.com",
        #     user_type=UserType.NGUOI_DUNG
        # )
        # db.session.add_all([user1,user2,user3,user4])
        # db.session.commit()
        pass