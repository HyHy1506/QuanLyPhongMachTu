# QuanLyPhongMachTu

Bước 1 : tạo database mới:

    - xóa cái cũ đi , tạo cái mới ,tạo thủ công database quanlyphongmachtudb 
    - chạy file phongmachtudb.sql trong MySQL Workbench để khởi tạo bảng và giá trị

Bước 2 : Đăng nhập tài khoản hoặc tạo mới để truy cập vào từng trang làm việc theo từng vai trò người dùng:

    - tài khoản bác sĩ :                    tên đăng nhập: bacsi , mật khẩu: 123
    - tài khoản người dùng khám bệnh :      tên đăng nhập: benhnhan , mật khẩu: 123
    - tài khoản y tá :                      tên đăng nhập: yta , mật khẩu: 123

    Đăng nhập đúng tài khoản sẽ tự động đi đến trang làm việc

Bước 3: Để lấy thông tin người dùng hiện tại đang đăng nhập , sử dụng :
    
    thêm current_user : from flask_login import current_user

    kiểm tra đã có người dùng đăng nhập chưa:
        
        if(current_user.is_authenticated):
            return redirect("/")

    lấy kiểu người dùng : current_user.user_type
    lấy id user : current_user.id
    lấy user name : current_user.username

    lấy được id user rồi thì sẽ truy vấn trong database để tìm user bằng hàm : get_user_by_id(userId)

Thông tin thêm :

Ứng dụng đã định nghĩa UserType trong models.py, gồm các loại:

    BAC_SI: Bác sĩ
    Y_TA: Y tá
    QUAN_TRI_VIEN: Quản trị viên
    NGUOI_DUNG: Người dùng thông thường

Các route tương ứng trong index.py:

    /doctor: Trang cho bác sĩ
    /nurse: Trang cho y tá
    /admin: Trang quản trị viên
    /user-patient: Trang người dùng thông thường

Viết hàm sử lý database trong thư mục dao/
