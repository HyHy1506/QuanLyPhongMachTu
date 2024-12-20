from flask_login import current_user,login_user,logout_user
from flask import render_template, request, redirect, url_for, session
from phongmachapp.dao.dao_admin import monthly_revenue, day_revenue, monthly_medicine
from MyPhongMAch.phongmachapp.models import UserType
from phongmachapp import  app,db
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
import json
from phongmachapp.models import User,Medicine,MedicalExaminationForm,MedicalExaminationFormDetail,PatientListDetail,PatientList,PaymentInvoice,Unit

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
            # neu chua dang nhap
        if not current_user.is_authenticated:
            return redirect('/')
            # neu khong phai quan tri vien
        if current_user.user_type != UserType.QUAN_TRI_VIEN:
            return redirect('/')

        return self.render("admin/index.html",report=day_revenue())

admin= Admin(app, name='Phòng mạch ĐGĐ', template_mode='bootstrap4',index_view=MyAdminIndexView())
# admin= Admin(app, name='Phòng mạch ĐGĐ', template_mode='bootstrap4')

class AuthenticateAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == UserType.QUAN_TRI_VIEN
class AuthenticateAdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == UserType.QUAN_TRI_VIEN
class UserView(AuthenticateAdminView):
    column_list = ["id", "username", "full_name", "is_male", "phone_number", "email", "user_type", "avatar"]
    form_columns = ["username", "password", "full_name", "is_male", "phone_number", "email", "user_type", "avatar"]
    column_searchable_list = ["username", "full_name", "email", "phone_number"]
    column_filters = ["user_type", "is_male"]
    # Định dạng cột avatar để hiển thị hình ảnh
    column_formatters = {
        "avatar": lambda view, context, model, name: Markup(
            f'<img src="{model.avatar}" style="width: 50px; height: 50px; border-radius: 50%;">'
        )
    }

class MedicineView(AuthenticateAdminView):
    column_list = ["id", "name", "unit_id", "price", "inventory_quantity"]
    form_columns = ["name", "unit_id", "price", "inventory_quantity"]
    column_searchable_list = ["name"]
    column_filters = ["unit_id"]

class PatientListView(AuthenticateAdminView):
    column_list = ["id", "created_date", "appointment_date", "nurse_id"]
    form_columns = ["created_date", "appointment_date", "nurse_id"]
    column_searchable_list = ["id", "nurse_id"]
    column_filters = ["appointment_date"]

class UnitView(AuthenticateAdminView):
    column_list = ["id", "name"]
    form_columns = ["name"]
    column_searchable_list = ["id", "name"]
    column_filters = ["name"]

class PaymentInvoiceView(AuthenticateAdminView):
    column_list = ["id", "medical_fee", "medicine_price", "cashier_id", "medical_examination_form_id"]
    form_columns = ["medical_fee", "medicine_price", "cashier_id", "medical_examination_form_id"]
    column_searchable_list = ["id", "cashier_id", "medical_examination_form_id"]
    column_filters = ["medical_fee", "medicine_price"]

class MedicalExaminationFormView(AuthenticateAdminView):
    column_list = ["id", "appointment_date", "symptom", "predicted_disease", "doctor_id", "patient_id"]
    form_columns = ["appointment_date", "symptom", "predicted_disease", "doctor_id", "patient_id"]
    column_searchable_list = ["symptom", "predicted_disease", "doctor_id", "patient_id"]
    column_filters = ["appointment_date", "doctor_id", "patient_id"]

class MedicalExaminationFormDetailView(AuthenticateAdminView):
    column_list = ["id", "quantity", "how_to_use", "medical_examination_form_id", "medicine_id"]
    form_columns = ["quantity", "how_to_use", "medical_examination_form_id", "medicine_id"]
    column_searchable_list = ["how_to_use"]
    column_filters = ["medicine_id", "medical_examination_form_id"]

class PatientListDetailView(AuthenticateAdminView):
    column_list = ["id", "patient_list_id", "user_id"]
    form_columns = ["patient_list_id", "user_id"]
    column_searchable_list = ["user_id"]
    column_filters = ["patient_list_id"]

class PatientListView(AuthenticateAdminView):
    column_list = ["id", "created_date", "appointment_date", "nurse_id"]
    form_columns = ["created_date", "appointment_date", "nurse_id"]
    column_searchable_list = ["id", "nurse_id"]
    column_filters = ["appointment_date", "nurse_id"]
class MonthlyRevenueView(AuthenticateAdminBaseView):
    @expose("/",methods=["GET","POST"])
    def index(self):
        list_month=list(range(1,13))
        list_year=list(range(2010,2025))
        list_year.reverse()
        selected_month = 11
        selected_year = 2024
        if request.method == "POST":
            selected_month=request.form.get("month")
            selected_year=request.form.get("year")

        report = monthly_revenue(month=selected_month, year=selected_year)
        list_revenues = [item['revenue'] for item in report['data']]
        list_day = [f"ngày {item['day'].day}" for item in report['data']]
        list_quantity_patient=[item['num_patients'] for item in report['data']]
        return self.render("admin/monthly_revenue.html"
                           ,list_month=list_month
                           ,list_year=list_year
                           ,selected_month=selected_month
                           ,selected_year=selected_year
                           ,report=report
                           ,list_revenues=list_revenues
                           ,list_day=list_day
                           ,list_quantity_patient=list_quantity_patient)
class MonthlyMedicineView(AuthenticateAdminBaseView):
    @expose("/",methods=['GET','POST'])
    def index(self):
        list_month = list(range(1, 13))
        list_year = list(range(2010, 2025))
        list_year.reverse()
        selected_month = 11
        selected_year = 2024
        if request.method == "POST":
            selected_month = request.form.get("month")
            selected_year = request.form.get("year")
        report = monthly_medicine(month=selected_month, year=selected_year)


        return self.render("admin/monthly_medicine.html",
                           list_month=list_month,
                           list_year = list_year,
                           selected_month = selected_month,
                           selected_year = selected_year,
                           report=report,
                          )

class LogoutView(AuthenticateAdminBaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/")

admin.add_view(UserView(User, db.session,name="Quản lý người dùng"))
admin.add_view(UnitView(Unit, db.session,name="Quản lý đơn vị"))
admin.add_view(MedicineView(Medicine, db.session,name="Quản lý thuốc"))
admin.add_view(MedicalExaminationFormView(MedicalExaminationForm, db.session,name="Phiếu khám bệnh"))
admin.add_view(MedicalExaminationFormDetailView(MedicalExaminationFormDetail, db.session,name="Chi tiết phiếu khám bệnh"))
admin.add_view(PatientListDetailView(PatientListDetail, db.session,name="Danh sách khám"))
admin.add_view(PatientListView(PatientList, db.session,name="Chi tiết danh sách khám"))
admin.add_view(PaymentInvoiceView(PaymentInvoice, db.session,name="Hóa đơn"))
admin.add_view(MonthlyRevenueView(name="Thống kê doanh thu theo tháng"))
admin.add_view(MonthlyMedicineView(name="Thống kê sử dụng thuốc theo tháng"))
admin.add_view(LogoutView(name="Đăng xuất"))

