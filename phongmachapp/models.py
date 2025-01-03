import enum
import hashlib
from tkinter.font import names
from sqlalchemy import text
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Boolean, DateTime, func, text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from phongmachapp import app, db
from flask_login import UserMixin


class UserType(str, enum.Enum):
    NGUOI_DUNG = "NGUOI_DUNG"
    BAC_SI = "BAC_SI"
    Y_TA = "Y_TA"
    QUAN_TRI_VIEN = "QUAN_TRI_VIEN"
    THU_NGAN = "THU_NGAN"


class TimeFrame(enum.Enum):
    SANG = "SANG"
    CHIEU = "CHIEU"
    TOI = "TOI"


class Unit(db.Model):
    __tablename__ = 'unit'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    # Relationships
    medicine_details = relationship('MedicalExaminationFormDetail', backref='unit', lazy=True)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('year_of_birth >= 1900', name='check_valid_birth_year'),
        {'extend_existing': True}
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_male = Column(Boolean, default=True)
    year_of_birth = Column(Integer, default=2000)
    phone_number = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    address = Column(String(100), default='TP.Hồ Chí Minh')
    user_type = Column(Enum(UserType), nullable=False, default=UserType.NGUOI_DUNG)
    avatar = Column(String(255),
                   default='https://res.cloudinary.com/df5wj9kts/image/upload/v1732882958/awhckz70evr3mmbsgf77.png')

    # Relationships
    waiting_lists = relationship('WaitingList', backref='user', lazy=True)
    patient_list_details = relationship('PatientListDetail', backref='patient', lazy=True)
    medical_examinations_as_doctor = relationship('MedicalExaminationForm',
                                                foreign_keys='MedicalExaminationForm.doctor_id',
                                                backref='doctor', lazy=True)
    medical_examinations_as_patient = relationship('MedicalExaminationForm',
                                                 foreign_keys='MedicalExaminationForm.patient_id',
                                                 backref='patient', lazy=True)
    payments_as_cashier = relationship('PaymentInvoice', backref='cashier', lazy=True)


class WaitingList(db.Model):
    __tablename__ = 'waitinglist'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    time_frame = Column(Enum(TimeFrame), default=TimeFrame.SANG, nullable=False)
    appointment_date = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)


class PatientList(db.Model):
    __tablename__ = 'patient_list'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=func.now())
    appointment_date = Column(DateTime, default=func.now())
    nurse_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    details = relationship('PatientListDetail', backref='patient_list', lazy=True)


class PatientListDetail(db.Model):
    __tablename__ = 'patient_list_detail'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_list_id = Column(Integer, ForeignKey('patient_list.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)


class MedicalExaminationForm(db.Model):
    __tablename__ = 'medical_examination_form'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_date = Column(DateTime, default=func.now())
    symptom = Column(String(255), nullable=True)
    predicted_disease = Column(String(255), nullable=True)
    doctor_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    patient_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    details = relationship('MedicalExaminationFormDetail', backref='examination_form', lazy=True)
    payment = relationship('PaymentInvoice', backref='examination_form', uselist=False, lazy=True)


class MedicalExaminationFormDetail(db.Model):
    __tablename__ = 'medical_examination_form_detail'
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_quantity'),
        {'extend_existing': True}
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_id = Column(Integer, ForeignKey('unit.id', ondelete='CASCADE'), default=1)
    how_to_use = Column(String(255), nullable=False)
    medical_examination_form_id = Column(Integer, ForeignKey('medical_examination_form.id', ondelete='CASCADE'), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicine.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    medicine = relationship('Medicine', backref='examination_details', lazy=True)


class Medicine(db.Model):
    __tablename__ = 'medicine'
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_non_negative_price'),
        CheckConstraint('inventory_quantity >= 0', name='check_non_negative_inventory'),
        {'extend_existing': True}
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    inventory_quantity = Column(Integer, default=0, nullable=False)


class PaymentInvoice(db.Model):
    __tablename__ = 'payment_invoice'
    __table_args__ = (
        CheckConstraint('medical_fee >= 0', name='check_non_negative_medical_fee'),
        CheckConstraint('medicine_price >= 0', name='check_non_negative_medicine_price'),
        {'extend_existing': True}
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    medical_fee = Column(Float, default=0.0, nullable=False)
    medicine_price = Column(Float, default=0.0, nullable=False)
    cashier_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    medical_examination_form_id = Column(Integer, ForeignKey('medical_examination_form.id', ondelete='CASCADE'),
                                       nullable=False, unique=True)

def generate_sample_data():

    from random import randint, choice
    from sqlalchemy.sql import text
    import random
    from faker import Faker
    from datetime import datetime, timedelta
    fake = Faker(['vi_VN'])
    # Clear old data
    # db.session.execute(text('DELETE FROM payment_invoice'))
    # db.session.execute(text('DELETE FROM medical_examination_form_detail'))
    # db.session.execute(text('DELETE FROM medical_examination_form'))
    # db.session.execute(text('DELETE FROM patient_list_detail'))
    # db.session.execute(text('DELETE FROM patient_list'))
    # db.session.execute(text('DELETE FROM waitinglist'))
    # db.session.execute(text('DELETE FROM medicine'))
    # db.session.execute(text('DELETE FROM unit'))
    # db.session.execute(text('DELETE FROM users'))
    db.drop_all()
    db.session.commit()
    db.create_all()
    db.session.commit()
    # Create Units
    units = [Unit(name=name) for name in ["Viên", "Chai", "Vỉ", "Ống", "Gói", "Hộp"]]
    db.session.add_all(units)
    db.session.commit()

    # Create Users
    password = str(hashlib.md5("123".encode('utf-8')).hexdigest())

    # Admin
    admin = User(username="admin", password=password, full_name="Quản trị viên",
                 phone_number="0123456789", email="admin@gmail.com",
                 address="123 Nguyễn Văn Cừ, Q.5, TP.HCM", user_type=UserType.QUAN_TRI_VIEN)
    db.session.add(admin)

    # Doctors, Nurses, Patients
    doctors = [
        User(username=f"doctor{i}", password=password, full_name=f"Bác sĩ {i}",
             phone_number=f"09012345{i:02}", email=f"doctor{i}@gmail.com",
             address=f"{i} Nguyễn Văn Cừ, TP.HCM", user_type=UserType.BAC_SI)
        for i in range(1, 6)
    ]

    nurses = [
        User(username=f"nurse{i}", password=password, full_name=f"Y tá {i}",
             phone_number=f"09112345{i:02}", email=f"nurse{i}@gmail.com",
             address=f"{i} Nguyễn Thị Minh Khai, TP.HCM", user_type=UserType.Y_TA)
        for i in range(1, 3)
    ]

    patients = [
        User(username=f"patient{i}", password=password, full_name=fake.name(),
             phone_number=fake.phone_number(), email=f"patient{i}@gmail.com",
             address=f"{i} Lý Thường Kiệt, TP.HCM", user_type=UserType.NGUOI_DUNG,
             year_of_birth=fake.year(), is_male=random.choice([True, False])
             )
        for i in range(1, 101)
    ]

    db.session.add_all(doctors + nurses + patients)
    db.session.commit()

    doctor1 = User(username="bacsi", password=password, full_name="Bác sĩ An",
                   phone_number="0901234501", email="bs@gmail.com",
                   address="1 Nguyễn Văn Cừ, TP.HCM", user_type=UserType.BAC_SI)
    nurse1 = User(username="yta", password=password, full_name="Y tá Binh",
                  phone_number="0911234501", email="yta@gmail.com",
                  address="1 Nguyễn Thị Minh Khai, TP.HCM", user_type=UserType.Y_TA)
    patient1 = User(username="benhnhan", password=password, full_name="Bệnh nhân Le",
                    phone_number="0921234501", email="benh@gmail.com",
                    address="1 Lý Thường Kiệt, TP.HCM", user_type=UserType.NGUOI_DUNG)
    cashier1 = User(username="thungan", password=password, full_name="Thu ngan Van",
                    phone_number="0921234504", email="thungan@gmail.com",
                    address="1 Lý Thường Kiệt, TP.HCM", user_type=UserType.THU_NGAN)
    db.session.add(doctor1)
    db.session.add(nurse1)
    db.session.add(patient1)
    db.session.add(cashier1)
    db.session.commit()
    # Create Medicines
    medicines = [
        Medicine(name=name, price=randint(10000, 50000), inventory_quantity=randint(100, 500))
        for name in [
            "Paracetamol", "Aspirin", "Amoxicillin", "Cephalexin", "Efferalgan",
            "Panadol", "Ciprofloxacin", "Metronidazole", "Ibuprofen", "Tiffy",
            "Berberin", "Cimetidine", "Oresol", "Ceftriaxone", "Cefixime",
            "Loperamide", "Dexamethasone", "Omeprazole", "Clarithromycin", "Tramadol"
        ]
    ]
    db.session.add_all(medicines)
    db.session.commit()

    # Monthly data generation
    for month in range(1, 13):
        for day in range(1, 29):
            date = datetime(2024, month, day)

            # Create WaitingList
            waiting_lists = [
                WaitingList(time_frame=choice(list(TimeFrame)), appointment_date=date, user_id=choice(patients).id)
                for _ in range(10)
            ]
            db.session.add_all(waiting_lists)
            db.session.commit()

            # Create PatientList
            nurse = choice(nurses)
            patient_list = PatientList(created_date=date, appointment_date=date, nurse_id=nurse.id)
            db.session.add(patient_list)
            db.session.commit()

            # Create PatientListDetail
            patient_list_details = [
                PatientListDetail(patient_list_id=patient_list.id, user_id=choice(patients).id)
                for _ in range(10)
            ]
            db.session.add_all(patient_list_details)
            db.session.commit()

            # Create MedicalExaminationForm
            doctor = choice(doctors)
            medical_forms = [
                MedicalExaminationForm(
                    appointment_date=date,
                    symptom=symptom,
                    predicted_disease=disease,
                    doctor_id=doctor.id,
                    patient_id=choice(patients).id
                )
                for symptom, disease in [
                    ("Sốt, đau đầu, đau mỏi cơ", "Sốt xuất huyết"),
                    ("Ho khan, sốt nhẹ, khó thở", "Viêm phổi"),
                    ("Đau bụng, tiêu chảy, nôn mửa", "Ngộ độc thực phẩm"),
                    ("Ho kéo dài, đau họng, sốt", "Viêm họng"),
                    ("Đau ngực, ho có đờm hoặc máu", "Lao phổi"),
                    ("Ngứa, nổi mẩn đỏ, sưng phù", "Dị ứng"),
                    ("Đau đầu dữ dội, mệt mỏi, buồn nôn", "Đau nửa đầu"),
                    ("Chảy nước mũi, nghẹt mũi, đau nhức mặt", "Viêm xoang"),
                    ("Khó tiểu, đau khi tiểu", "Nhiễm trùng đường tiết niệu"),
                    ("Sụt cân, mệt mỏi, khát nước nhiều", "Tiểu đường")
                ]
            ]
            db.session.add_all(medical_forms)
            db.session.commit()

            # Create MedicalExaminationFormDetail and PaymentInvoice
            for form in medical_forms:
                details = [
                    MedicalExaminationFormDetail(quantity=randint(1, 5), unit_id=choice(units).id,
                                                 how_to_use="Dùng theo chỉ định bác sĩ",
                                                 medical_examination_form_id=form.id, medicine_id=choice(medicines).id)
                    for _ in range(10)
                ]
                db.session.add_all(details)

                invoice = PaymentInvoice(medical_fee=100000, medicine_price=randint(50000, 200000),
                                         cashier_id=admin.id, medical_examination_form_id=form.id)
                db.session.add(invoice)

            db.session.commit()



if __name__ == '__main__':
    with app.app_context():
        generate_sample_data()
        print("Đã tạo xong dữ liệu mẫu!")

