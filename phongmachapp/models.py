import enum
import hashlib
from tkinter.font import names

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Boolean, DateTime, func, text
from sqlalchemy.orm import relationship
from phongmachapp import app, db
from flask_login import UserMixin


class UserType(str, enum.Enum):
    NGUOI_DUNG = "NGUOI_DUNG"
    BAC_SI = "BAC_SI"
    Y_TA = "Y_TA"
    QUAN_TRI_VIEN = "QUAN_TRI_VIEN"

#
# class Unit(enum.Enum):
#     VIEN = "VIEN"
#     CHAI = "CHAI"
#     VI = "VI"


class TimeFrame(enum.Enum):
    SANG = "SANG"
    CHIEU = "CHIEU"
    TOI = "TOI"

class Unit(db.Model):
    __tablename__ = 'unit'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(100), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_male = Column(Boolean, default=True)
    year_of_birth = Column(Integer, default=2000)
    phone_number = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    user_type = Column(Enum(UserType), nullable=False, default=UserType.NGUOI_DUNG)
    avatar = Column(String(255),
                    default='https://res.cloudinary.com/df5wj9kts/image/upload/v1732882958/awhckz70evr3mmbsgf77.png')
# Danh sach cho
class WaitingList(db.Model):
    __tablename__ = 'waitinglist'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    time_frame = Column(Enum(TimeFrame), default=TimeFrame.SANG,nullable=False)
    appointment_date = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

# Danh sach kham benh
class PatientList(db.Model):
    __tablename__ = 'patient_list'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=func.now())
    appointment_date = Column(DateTime, default=func.now())
    nurse_id = Column(Integer, ForeignKey('users.id'), nullable=False)

# chi tiet danh sach kham benh
class PatientListDetail(db.Model):
    __tablename__ = 'patient_list_detail'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_list_id = Column(Integer, ForeignKey('patient_list.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

# Phieu kham benh
class MedicalExaminationForm(db.Model):
    __tablename__ = 'medical_examination_form'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_date = Column(DateTime, default=func.now())
    symptom = Column(String(255), nullable=True)
    predicted_disease = Column(String(255), nullable=True)
    doctor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('users.id'), nullable=False)

#Chi tiet phieu kham benh
class MedicalExaminationFormDetail(db.Model):
    __tablename__ = 'medical_examination_form_detail'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, default=1, nullable=False)
    how_to_use = Column(String(255), nullable=False)
    medical_examination_form_id = Column(Integer, ForeignKey('medical_examination_form.id'), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicine.id'), nullable=False)

# Thuoc
class Medicine(db.Model):
    __tablename__ = 'medicine'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    unit_id = Column(Integer, ForeignKey('unit.id'), default=1)
    price = Column(Float, nullable=False)
    inventory_quantity = Column(Integer, default=0, nullable=False)


# hoa don
class PaymentInvoice(db.Model):
    __tablename__ = 'payment_invoice'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    medical_fee = Column(Float, default=0.0, nullable=False)
    medicine_price = Column(Float, default=0.0, nullable=False)
    cashier_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    medical_examination_form_id = Column(Integer, ForeignKey('medical_examination_form.id'), nullable=False,primary_key=True)



if __name__ == '__main__':
    with app.app_context():
        # add sample data
        import random
        from faker import Faker
        from datetime import datetime, timedelta

        fake = Faker()


        def random_date(start_date, end_date):
            delta = end_date - start_date
            random_days = random.randint(0, delta.days)
            return start_date + timedelta(days=random_days)


        db.drop_all()
        db.create_all()
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        user1 = User(
            username="admin",
            password=password,
            full_name="Nguyen Van A",
            phone_number="0123456789",
            email="admin@gmail.com",
            user_type=UserType.QUAN_TRI_VIEN
        )
        user2 = User(
            username="bacsi",
            password=password,
            full_name="Nguyen Van B",
            phone_number="0123456789",
            email="doctor@gmail.com",
            user_type=UserType.BAC_SI
        )
        user3 = User(
            username="yta",
            password=password,
            full_name="Nguyen Van C",
            phone_number="0123456789",
            email="nurse@gmail.com",
            user_type=UserType.Y_TA
        )
        user4 = User(
            username="benhnhan",
            password=password,
            full_name="Nguyen Van D",
            phone_number="0123456789",
            email="patient@gmail.com",
            user_type=UserType.NGUOI_DUNG
        )
        db.session.add_all([user1, user2, user3, user4])
        db.session.commit()
        # add unit
        unit1=Unit(name="Chai")
        unit2=Unit(name="Viên")
        unit3=Unit(name="Vỉ")
        db.session.add_all([unit1, unit2, unit3])
        db.session.commit()
        # Add Users
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest())
        users = []
        users.append(user1)
        users.append(user2)
        users.append(user3)
        users.append(user4)
        for _ in range(20):
            user = User(
                username=fake.unique.user_name(),
                password=password,
                full_name=fake.name(),
                phone_number=fake.phone_number(),
                email=fake.unique.email(),
                user_type=random.choice(list(UserType)),
                is_male=random.choice([True, False]),
                year_of_birth = fake.year()

            )
            users.append(user)
        db.session.add_all(users)
        db.session.commit()  # Commit users to the database

        # add waitinglist
        waiting_list=[]
        for _ in range(120):
            waiting=WaitingList(
                time_frame=random.choice(list(TimeFrame)),
                appointment_date = random_date(datetime(2024, 1, 1), datetime(2024, 12, 31)),
                user_id = random.choice([user.id for user in users if user.user_type == UserType.NGUOI_DUNG])
            )
            waiting_list.append(waiting)
        db.session.add_all(waiting_list)
        db.session.commit()
        # Add Medicines
        medicines = []
        units=[1,2,3]
        for _ in range(20):
            medicine = Medicine(
                name=fake.unique.word(),
                unit_id=random.choice([pl for pl in units]),
                price=round(random.uniform(1, 100), 2),
                inventory_quantity=random.randint(0, 500)
            )
            medicines.append(medicine)
        db.session.add_all(medicines)
        db.session.commit()  # Commit medicines to the database

        # Add Patient Lists
        patient_lists = []
        for _ in range(60):
            patient_list = PatientList(
                created_date=random_date(datetime(2023, 1, 1), datetime(2024, 12, 31)),
                appointment_date=random_date(datetime(2024, 1, 1), datetime(2024, 12, 31)),
                nurse_id=random.choice([user.id for user in users if user.user_type == UserType.Y_TA])
            )
            patient_lists.append(patient_list)
        db.session.add_all(patient_lists)
        db.session.commit()  # Commit patient lists to the database

        # Add Medical Examination Forms
        medical_forms = []
        for _ in range(60):
            medical_form = MedicalExaminationForm(
                appointment_date=random_date(datetime(2024, 1, 1), datetime(2024, 12, 31)),
                symptom=fake.sentence(),
                predicted_disease=fake.word(),
                doctor_id=random.choice([user.id for user in users if user.user_type == UserType.BAC_SI]),
                patient_id=random.choice([user.id for user in users if user.user_type == UserType.NGUOI_DUNG])
            )
            medical_forms.append(medical_form)
        db.session.add_all(medical_forms)
        db.session.commit()  # Commit medical forms to the database

        # Add Medical Examination Form Details
        form_details = []
        for _ in range(120):
            form_detail = MedicalExaminationFormDetail(
                quantity=random.randint(1, 10),
                how_to_use=fake.sentence(),
                medical_examination_form_id=random.choice([pl.id for pl in medical_forms]),
                medicine_id=random.choice([med.id for med in medicines])
            )
            form_details.append(form_detail)
        db.session.add_all(form_details)
        db.session.commit()  # Commit form details to the database

        # Add Payment Invoices
        invoices = []
        used_medical_form_ids = set()  # Set để theo dõi các ID đã được sử dụng

        # Lặp qua tất cả các Medical Examination Forms để đảm bảo không trùng
        available_medical_form_ids = [form.id for form in medical_forms]
        for medical_form_id in available_medical_form_ids:
            invoice = PaymentInvoice(
                medical_fee=round(random.uniform(50, 500), 2),
                medicine_price=round(random.uniform(10, 200), 2),
                cashier_id=random.choice([user.id for user in users if user.user_type == UserType.QUAN_TRI_VIEN]),
                medical_examination_form_id=medical_form_id
            )
            invoices.append(invoice)

        db.session.add_all(invoices)
        db.session.commit()  # Commit invoices to the database

        # Add Patient List Details
        patient_list_details = []
        for _ in range(120):
            detail = PatientListDetail(
                patient_list_id=random.choice([pl.id for pl in patient_lists]),
                user_id=random.choice([user.id for user in users if user.user_type == UserType.NGUOI_DUNG])
            )
            patient_list_details.append(detail)
        db.session.add_all(patient_list_details)
        db.session.commit()
    pass
