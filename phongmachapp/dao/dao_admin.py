from click import group

from phongmachapp import db
from sqlalchemy import func
from phongmachapp.models import *
def monthly_revenue(month=None,year=None):
    data = db.session.query(
        func.date(MedicalExaminationForm.appointment_date).label("day"),
        func.count(MedicalExaminationForm.id).label("num_patients"),
        func.sum(PaymentInvoice.medical_fee + PaymentInvoice.medicine_price).label("revenue")
    ).join(
        PaymentInvoice,
        PaymentInvoice.medical_examination_form_id == MedicalExaminationForm.id
    ).group_by(
        func.date(MedicalExaminationForm.appointment_date)
    ).order_by(
        func.date(MedicalExaminationForm.appointment_date)
    )
    if month:
        data = data.filter(
        func.extract('month', MedicalExaminationForm.appointment_date) == month
    )
    if year:
        data = data.filter(
            func.extract('year', MedicalExaminationForm.appointment_date) == year
        )
    data= data.all()
    # Tính tổng doanh thu
    total_revenue = round(sum(item.revenue for item in data if item.revenue is not None),2)

    # Tính tỷ lệ doanh thu và định dạng kết quả
    result = []
    for index, item in enumerate(data, start=1):
        percentage = (item.revenue / total_revenue * 100) if total_revenue > 0 else 0
        result.append({
            "stt": index,
            "day": item.day,
            "num_patients": item.num_patients,
            "revenue": round( item.revenue,2),
            "percentage": round(percentage, 2)
        })

    return {
        "year": year,
        "month": month,
        "data": result,
        "total_revenue": total_revenue
    }

def day_revenue(day =None,month=None,year=None):
    data = (db.session.query(
        func.date(MedicalExaminationForm.appointment_date).label("day"),
        User.full_name.label("patient_name"),
        PaymentInvoice.medical_fee.label("medical_fee"),
        PaymentInvoice.medicine_price.label("medicine_price")
    ).select_from(MedicalExaminationForm)\
        .join(User, User.id == MedicalExaminationForm.patient_id) \
        .join(PaymentInvoice, PaymentInvoice.medical_examination_form_id == MedicalExaminationForm.id) \
        .order_by(func.date(MedicalExaminationForm.appointment_date)))
    return data.all()

def monthly_medicine(month=None,year=None):
    medical_examination_form_filter_month=db.session.query(
        MedicalExaminationForm.id,
    ).order_by(func.date(MedicalExaminationForm.appointment_date))
    if month:
        medical_examination_form_filter_month=medical_examination_form_filter_month.filter(
        func.extract('month', MedicalExaminationForm.appointment_date) == month
    )
    if year:
        medical_examination_form_filter_month = medical_examination_form_filter_month.filter(
                func.extract('year', MedicalExaminationForm.appointment_date) == year
            )
    medical_examination_form_filter_month=medical_examination_form_filter_month.subquery()
    data = db.session.query(
        MedicalExaminationFormDetail.medicine_id,
        Medicine.name,
        Unit.name,
        func.sum(MedicalExaminationFormDetail.quantity),
        func.count(MedicalExaminationFormDetail.medicine_id),

    ).select_from(MedicalExaminationFormDetail)\
    .join(medical_examination_form_filter_month,
          MedicalExaminationFormDetail.medical_examination_form_id == medical_examination_form_filter_month.c.id)\
    .join(Medicine,Medicine.id == MedicalExaminationFormDetail.medicine_id)\
    .join(Unit,Unit.id == Medicine.unit_id)\
    .group_by(MedicalExaminationFormDetail.medicine_id)\


    return data.all()

