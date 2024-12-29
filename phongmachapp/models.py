import enum
import hashlib
from tkinter.font import names
from sqlalchemy import text
from datetime import datetime
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
    address =Column(String(100),default='TP.Hồ Chí Minh')
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
    unit_id = Column(Integer, ForeignKey('unit.id'), default=1)
    how_to_use = Column(String(255), nullable=False)
    medical_examination_form_id = Column(Integer, ForeignKey('medical_examination_form.id'), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicine.id'), nullable=False)

# Thuoc
class Medicine(db.Model):
    __tablename__ = 'medicine'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
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


def generate_sample_data():
    # Xóa dữ liệu cũ
    db.session.execute(text('DELETE FROM payment_invoice'))
    db.session.execute(text('DELETE FROM medical_examination_form_detail'))
    db.session.execute(text('DELETE FROM medical_examination_form'))
    db.session.execute(text('DELETE FROM patient_list_detail'))
    db.session.execute(text('DELETE FROM patient_list'))
    db.session.execute(text('DELETE FROM waitinglist'))
    db.session.execute(text('DELETE FROM medicine'))
    db.session.execute(text('DELETE FROM unit'))
    db.session.execute(text('DELETE FROM users'))
    db.session.commit()

    # Tạo Units
    unit1 = Unit(name="Viên")
    unit2 = Unit(name="Chai")
    unit3 = Unit(name="Vỉ")
    unit4 = Unit(name="Ống")
    unit5 = Unit(name="Gói")
    unit6 = Unit(name="Hộp")
    db.session.add_all([unit1, unit2, unit3, unit4, unit5, unit6])
    db.session.commit()

    # Tạo Users
    password = str(hashlib.md5("123".encode('utf-8')).hexdigest())

    # Admin
    admin = User(username="admin", password=password, full_name="Quản trị viên",
                 phone_number="0123456789", email="admin@gmail.com",
                 address="123 Nguyễn Văn Cừ, Q.5, TP.HCM", user_type=UserType.QUAN_TRI_VIEN)

    # Bác sĩ
    doctor1 = User(username="bacsi", password=password, full_name="Nguyễn Văn An",
                   phone_number="0901234567", email="doctor1@gmail.com",
                   address="45 CMT8, Q.3, TP.HCM", user_type=UserType.BAC_SI)
    doctor2 = User(username="doctor2", password=password, full_name="Trần Thị Bình",
                   phone_number="0901234568", email="doctor2@gmail.com",
                   address="67 Lê Lợi, Q.1, TP.HCM", user_type=UserType.BAC_SI)
    doctor3 = User(username="doctor3", password=password, full_name="Phạm Văn Cường",
                   phone_number="0901234569", email="doctor3@gmail.com",
                   address="89 Nguyễn Huệ, Q.1, TP.HCM", user_type=UserType.BAC_SI)

    # Y tá
    nurse1 = User(username="yta", password=password, full_name="Lê Thị Dung",
                  phone_number="0911234567", email="nurse1@gmail.com",
                  address="12 Trần Hưng Đạo, Q.5, TP.HCM", user_type=UserType.Y_TA)
    nurse2 = User(username="nurse2", password=password, full_name="Hoàng Văn Em",
                  phone_number="0911234568", email="nurse2@gmail.com",
                  address="34 Hai Bà Trưng, Q.1, TP.HCM", user_type=UserType.Y_TA)

    # Bệnh nhân
    patient1 = User(username="benhnhan", password=password, full_name="Trương Văn Phi",
                    phone_number="0921234567", email="patient1@gmail.com",
                    address="56 Lý Thường Kiệt, Q.10, TP.HCM", user_type=UserType.NGUOI_DUNG)
    patient2 = User(username="patient2", password=password, full_name="Ngô Thị Giang",
                    phone_number="0921234568", email="patient2@gmail.com",
                    address="78 Nguyễn Du, Q.1, TP.HCM", user_type=UserType.NGUOI_DUNG)
    patient3 = User(username="patient3", password=password, full_name="Đặng Văn Hùng",
                    phone_number="0921234569", email="patient3@gmail.com",
                    address="90 Võ Văn Tần, Q.3, TP.HCM", user_type=UserType.NGUOI_DUNG)
    patient4 = User(username="patient4", password=password, full_name="Bùi Thị Ian",
                    phone_number="0921234570", email="patient4@gmail.com",
                    address="123 Điện Biên Phủ, Q.Bình Thạnh, TP.HCM", user_type=UserType.NGUOI_DUNG)
    patient5 = User(username="patient5", password=password, full_name="Phan Văn Khôi",
                    phone_number="0921234571", email="patient5@gmail.com",
                    address="456 Nguyễn Thị Minh Khai, Q.3, TP.HCM", user_type=UserType.NGUOI_DUNG)

    db.session.add_all([admin, doctor1, doctor2, doctor3, nurse1, nurse2,
                        patient1, patient2, patient3, patient4, patient5])
    db.session.commit()

    # Tạo Medicines
    med1 = Medicine(name="Paracetamol", price=15000, inventory_quantity=500)
    med2 = Medicine(name="Amoxicillin", price=25000, inventory_quantity=400)
    med3 = Medicine(name="Omeprazole", price=35000, inventory_quantity=300)
    med4 = Medicine(name="Vitamin C", price=45000, inventory_quantity=600)
    med5 = Medicine(name="Aspirin", price=12000, inventory_quantity=450)
    db.session.add_all([med1, med2, med3, med4, med5])
    db.session.commit()

    # Tạo WaitingList
    wait1 = WaitingList(time_frame=TimeFrame.SANG, appointment_date=datetime(2024, 3, 1), user_id=patient1.id)
    wait2 = WaitingList(time_frame=TimeFrame.CHIEU, appointment_date=datetime(2024, 3, 1), user_id=patient2.id)
    wait3 = WaitingList(time_frame=TimeFrame.TOI, appointment_date=datetime(2024, 3, 2), user_id=patient3.id)
    wait4 = WaitingList(time_frame=TimeFrame.SANG, appointment_date=datetime(2024, 3, 2), user_id=patient4.id)
    wait5 = WaitingList(time_frame=TimeFrame.CHIEU, appointment_date=datetime(2024, 3, 3), user_id=patient5.id)
    db.session.add_all([wait1, wait2, wait3, wait4, wait5])
    db.session.commit()

    # Tạo PatientList
    plist1 = PatientList(created_date=datetime(2024, 3, 1), appointment_date=datetime(2024, 3, 1), nurse_id=nurse1.id)
    plist2 = PatientList(created_date=datetime(2024, 3, 2), appointment_date=datetime(2024, 3, 2), nurse_id=nurse2.id)
    plist3 = PatientList(created_date=datetime(2024, 3, 3), appointment_date=datetime(2024, 3, 3), nurse_id=nurse1.id)
    db.session.add_all([plist1, plist2, plist3])
    db.session.commit()

    # Tạo PatientListDetail
    pld1 = PatientListDetail(patient_list_id=plist1.id, user_id=patient1.id)
    pld2 = PatientListDetail(patient_list_id=plist1.id, user_id=patient2.id)
    pld3 = PatientListDetail(patient_list_id=plist2.id, user_id=patient3.id)
    pld4 = PatientListDetail(patient_list_id=plist2.id, user_id=patient4.id)
    pld5 = PatientListDetail(patient_list_id=plist3.id, user_id=patient5.id)
    db.session.add_all([pld1, pld2, pld3, pld4, pld5])
    db.session.commit()

    # Tạo MedicalExaminationForm
    mef1 = MedicalExaminationForm(appointment_date=datetime(2024, 3, 1),
                                  symptom="Sốt, ho", predicted_disease="Cảm cúm",
                                  doctor_id=doctor1.id, patient_id=patient1.id)
    mef2 = MedicalExaminationForm(appointment_date=datetime(2024, 3, 1),
                                  symptom="Đau đầu", predicted_disease="Thiếu máu não",
                                  doctor_id=doctor2.id, patient_id=patient2.id)
    mef3 = MedicalExaminationForm(appointment_date=datetime(2024, 3, 2),
                                  symptom="Đau bụng", predicted_disease="Viêm dạ dày",
                                  doctor_id=doctor3.id, patient_id=patient3.id)
    db.session.add_all([mef1, mef2, mef3])
    db.session.commit()

    # Tạo MedicalExaminationFormDetail
    mefd1 = MedicalExaminationFormDetail(quantity=2, unit_id=unit1.id,
                                         how_to_use="Uống 1 viên sau khi ăn",
                                         medical_examination_form_id=mef1.id, medicine_id=med1.id)
    mefd2 = MedicalExaminationFormDetail(quantity=1, unit_id=unit2.id,
                                         how_to_use="Uống 1 chai mỗi sáng",
                                         medical_examination_form_id=mef1.id, medicine_id=med2.id)
    mefd3 = MedicalExaminationFormDetail(quantity=3, unit_id=unit3.id,
                                         how_to_use="Uống 1 vỉ mỗi tối",
                                         medical_examination_form_id=mef2.id, medicine_id=med3.id)
    mefd4 = MedicalExaminationFormDetail(quantity=2, unit_id=unit4.id,
                                         how_to_use="Uống 1 ống mỗi ngày",
                                         medical_examination_form_id=mef3.id, medicine_id=med4.id)
    db.session.add_all([mefd1, mefd2, mefd3, mefd4])
    db.session.commit()

    # Tạo PaymentInvoice
    inv1 = PaymentInvoice(medical_fee=100000, medicine_price=150000,
                          cashier_id=admin.id, medical_examination_form_id=mef1.id)
    inv2 = PaymentInvoice(medical_fee=100000, medicine_price=200000,
                          cashier_id=admin.id, medical_examination_form_id=mef2.id)
    inv3 = PaymentInvoice(medical_fee=100000, medicine_price=250000,
                          cashier_id=admin.id, medical_examination_form_id=mef3.id)
    db.session.add_all([inv1, inv2, inv3])
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        generate_sample_data()
        print("Đã tạo xong dữ liệu mẫu!")

