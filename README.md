# 📚 ระบบยืม-คืนหนังสือห้องสมุด (Library Management System)

ระบบจัดการห้องสมุดสำหรับโรงเรียน พัฒนาด้วย **Django Framework** ครอบคลุมการสมัครสมาชิก
ค้นหา/ยืม/คืนหนังสือ ระบบจองคิวเมื่อหนังสือหมด คำนวณค่าปรับอัตโนมัติ และหลังบ้านสำหรับ
ผู้ดูแลระบบ (บรรณารักษ์) ใช้จัดการหนังสือ สมาชิก และดูรายงานสถิติ

ออกแบบตาม **ER Diagram** และ **Flowchart** ที่ทีมออกแบบไว้ (ดูหัวข้อ "โครงสร้างระบบ" ด้านล่าง)

---

## 🧱 เทคโนโลยีที่ใช้

| ส่วนประกอบ | เทคโนโลยี |
|---|---|
| Backend | Python 3.10+ / Django 5.0 |
| Database | SQLite (พัฒนา) — เปลี่ยนเป็น PostgreSQL/MySQL ได้ตอน deploy จริง |
| Frontend | Django Template + Bootstrap 5 + CSS ธีมกำหนดเอง |
| Auth | Django Authentication System (Session-based Login) |
| Version Control | Git + GitHub |

---

## 📂 โครงสร้างโปรเจกต์

```
library_project/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── library_project/          # การตั้งค่าหลักของโปรเจกต์ (settings, urls)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                 # แอปจัดการสมาชิก/แอดมิน + ระบบล็อกอิน
│   ├── models.py             # Member, AdminProfile
│   ├── forms.py              # ฟอร์มสมัครสมาชิก
│   ├── views.py              # login/register/dashboard router
│   └── urls.py
├── library/                  # แอปหลักของระบบห้องสมุด
│   ├── models.py             # Book, Borrow, Return, Reservation, Report
│   ├── forms.py
│   ├── views.py              # ยืม/คืน/จอง/จัดการหนังสือ/รายงาน
│   ├── urls.py
│   └── management/commands/seed_demo.py   # คำสั่งสร้างข้อมูลตัวอย่าง
├── templates/                 # ไฟล์ HTML ทั้งหมด (Django Template)
│   ├── base.html
│   ├── registration/login.html
│   ├── accounts/
│   │   ├── register.html
│   │   ├── member_dashboard.html
│   │   └── admin_dashboard.html
│   └── library/
│       ├── book_list.html
│       ├── my_borrows.html
│       ├── my_reservations.html
│       ├── admin_book_list.html
│       ├── admin_book_form.html
│       ├── admin_member_list.html
│       ├── admin_transactions.html
│       └── admin_reports.html
└── static/css/style.css       # ธีมสี / ดีไซน์ของเว็บ
```

---

## 🗂️ โครงสร้างระบบ (ตาม ER Diagram)

| ตาราง | หน้าที่ |
|---|---|
| **Member** | ข้อมูลสมาชิก (นักเรียน) — เชื่อมกับ `User` ของ Django สำหรับล็อกอิน |
| **AdminProfile** | ข้อมูลผู้ดูแลระบบ/บรรณารักษ์ — เชื่อมกับ `User` เช่นกัน |
| **Book** | ข้อมูลหนังสือ (ISBN, ผู้แต่ง, จำนวนคงเหลือ ฯลฯ) |
| **Borrow** | รายการยืมหนังสือ (1 สมาชิก ยืมได้หลายเล่ม, 1 เล่ม ถูกยืมได้หลายครั้ง) |
| **Return** | รายการคืนหนังสือ ผูกกับ Borrow แบบ 1:1 พร้อมคำนวณค่าปรับ |
| **Reservation** | คิวจองหนังสือเมื่อหนังสือหมด |
| **Report** | บันทึกรายงานที่แอดมินสร้าง |

ตรรกะการทำงานอ้างอิงจาก **Flowchart**:
- เข้าสู่ระบบ → แยกเมนูสมาชิก / เมนูแอดมิน / สมัครสมาชิก
- สมาชิก: ค้นหาหนังสือ → ถ้ามีสต็อก ยืมได้ทันที (ตรวจโควตา/ค่าปรับค้างก่อน) → ถ้าไม่มีสต็อก เข้าคิวจอง
- คืนหนังสือ → คำนวณวันเกินกำหนด → คิดค่าปรับ → คืนจำนวนสต็อก +1 → ถ้ามีคิวจอง แจ้งเตือนคิวถัดไปอัตโนมัติ
- แอดมิน: จัดการหนังสือ/สมาชิก/ตรวจสอบรายการยืม-คืน/ออกรายงาน

---

## 🚀 วิธีติดตั้งและรันโปรแกรม (ทีละขั้นตอน)

### 1. ติดตั้งเครื่องมือที่ต้องมี
- Python 3.10 ขึ้นไป → https://www.python.org/downloads/
- Git → https://git-scm.com/downloads
- VS Code → https://code.visualstudio.com/

### 2. Clone โปรเจกต์จาก GitHub
```bash
git clone https://github.com/<ชื่อกลุ่ม>/library-management-system.git
cd library-management-system
```

### 3. สร้าง Virtual Environment (แนะนำ)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. ติดตั้งไลบรารีที่จำเป็น
```bash
pip install -r requirements.txt
```

### 5. สร้างฐานข้อมูล (Migrate)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. สร้างข้อมูลตัวอย่าง (บัญชีทดสอบ + หนังสือตัวอย่าง)
```bash
python manage.py seed_demo
```
คำสั่งนี้จะสร้างให้อัตโนมัติ:
- แอดมิน: `admin` / `admin1234`
- สมาชิกทดสอบ: `student1` `student2` `student3` (รหัสผ่าน `student1234`)
- หนังสือตัวอย่าง 8 เล่ม

หรือจะสร้างผู้ดูแลระบบเองก็ได้ด้วยคำสั่ง:
```bash
python manage.py createsuperuser
```
(หลังสร้างแล้ว ต้องเข้า Django Admin ที่ `/admin/` เพื่อเพิ่มข้อมูลใน `AdminProfile` ผูกกับ user นั้นด้วย)

### 7. รันเซิร์ฟเวอร์
```bash
python manage.py runserver
```
เปิดเบราว์เซอร์ไปที่ **http://127.0.0.1:8000/**

### 8. เข้าใช้งาน
- หน้าเว็บหลัก → ล็อกอิน หรือกด "สมัครสมาชิกใหม่"
- ล็อกอินด้วยบัญชี `admin` เพื่อเข้าหลังบ้านจัดการระบบ
- ล็อกอินด้วยบัญชี `student1` เพื่อทดลองยืม-คืนหนังสือฝั่งสมาชิก

---

## ⚙️ ค่าที่ปรับได้ (business rule)

ไฟล์ `library/models.py` ด้านบนสุด:
```python
BORROW_DAYS = 7          # ยืมได้กี่วันก่อนครบกำหนด
FINE_PER_DAY = 5.00       # ค่าปรับต่อวัน (บาท)
MAX_BORROW_LIMIT = 5      # ยืมพร้อมกันได้สูงสุดกี่เล่ม
```

---

## 👥 การทำงานเป็นทีม (4 คน) ด้วย Git/GitHub

### แบ่งหน้าที่แนะนำ (ปรับตามความถนัดของทีมได้)
| สมาชิก | ผิดชอบ Branch | หน้าที่ |
|---|---|---|
| คนที่ 1 ตะวัน รุ่งโรจน์รัตน์ | `feature/accounts` | ระบบ Login/Register, Member, AdminProfile |
| คนที่ 2 ณัฐพล ทระคำไพ | `feature/book-catalog` | จัดการหนังสือ (CRUD), ค้นหาหนังสือ |
| คนที่ 3 ณัฐรัตน์ อ่วมขยัน | `feature/borrow-return` | ระบบยืม-คืน, คำนวณค่าปรับ, ระบบจองคิว |
| คนที่ 4 สิริวิวัฒน์ วรวิพัฒนะ | `feature/admin-dashboard` | แดชบอร์ดแอดมิน, รายงานสถิติ, UI/UX |

### ขั้นตอนการทำงานร่วมกัน
```bash
# 1. Clone ครั้งแรก (ทำครั้งเดียว)
git clone https://github.com/<ชื่อกลุ่ม>/library-management-system.git
cd library-management-system

# 2. สร้าง branch ของตัวเอง จาก main
git checkout main
git pull origin main
git checkout -b feature/ชื่อฟีเจอร์ของคุณ

# 3. ทำงาน แก้ไขไฟล์ แล้ว commit เป็นระยะ (commit บ่อย ๆ มีคำอธิบายชัดเจน)
git add .
git commit -m "feat: เพิ่มฟอร์มค้นหาหนังสือตามหมวดหมู่"

# 4. Push ขึ้น branch ของตัวเองบน GitHub
git push origin feature/ชื่อฟีเจอร์ของคุณ

# 5. เปิด Pull Request บน GitHub เพื่อขอรวมเข้า main
#    ให้เพื่อนในทีมอย่างน้อย 1 คน review ก่อน merge

# 6. หลัง merge แล้ว อัปเดต main ในเครื่องตัวเอง
git checkout main
git pull origin main
```

### รูปแบบข้อความ Commit ที่แนะนำ
```
feat: เพิ่มฟีเจอร์ใหม่           เช่น feat: เพิ่มระบบจองคิวหนังสือ
fix: แก้บั๊ก                     เช่น fix: แก้ไขการคำนวณค่าปรับผิดพลาด
docs: แก้ไขเอกสาร                เช่น docs: อัปเดตขั้นตอนติดตั้งใน README
style: ปรับ UI/CSS               เช่น style: ปรับสีปุ่มหน้ายืมหนังสือ
refactor: ปรับโครงสร้างโค้ด      เช่น refactor: แยกฟังก์ชันคำนวณค่าปรับ
```

### เงื่อนไขที่ควรทำให้ครบตามใบงาน
- [ ] สร้าง Repository บน GitHub และเชิญสมาชิกทุกคนเป็น Collaborator
- [ ] สมาชิกแต่ละคนสร้าง Branch ของตัวเอง (อย่างน้อย 4 branch ตามจำนวนสมาชิก)
- [ ] ทุก branch ต้องถูก merge กลับเข้า `main` ผ่าน Pull Request
- [ ] มีประวัติ commit ของสมาชิกทุกคนใน GitHub (ไม่ใช่คนเดียว push ทั้งหมด)
- [ ] อัปเดตความคืบหน้าใน Padlet (Timeline) อย่างต่อเนื่อง
- [ ] แนบไฟล์ `Backup.zip` ที่สมบูรณ์พร้อมใช้งาน (โฟลเดอร์นี้บีบอัดทั้งหมด)

---

## 🧪 การทดสอบเบื้องต้นที่ทำแล้ว
โปรแกรมผ่านการทดสอบ end-to-end ด้วย Django Test Client แล้วในสถานการณ์:
- ล็อกอิน/สมัครสมาชิก/ออกจากระบบ
- ยืมหนังสือ (กรณีมีสต็อก) และคืนหนังสือ พร้อมคำนวณค่าปรับเมื่อเกินกำหนด
- ยืมหนังสือจนสต็อกหมด → ระบบสร้างคิวจองอัตโนมัติ
- คืนหนังสือแล้วระบบแจ้งเตือนคิวจองลำดับถัดไปโดยอัตโนมัติ
- แอดมิน: เพิ่ม/แก้ไข/ลบหนังสือ, ระงับ/ปลดระงับสมาชิก, ดูรายงานสถิติ

แนะนำให้แต่ละคนในทีมทดสอบเพิ่มเติมตามฟีเจอร์ที่ตนรับผิดชอบ ก่อน merge เข้า `main`

---

## 📌 สิ่งที่ควรทำต่อก่อน deploy ใช้งานจริง
1. เปลี่ยน `DEBUG = False` และตั้งค่า `DJANGO_ALLOWED_HOSTS` เป็นโดเมนจริง (ตั้งผ่าน environment variable)
2. ตั้งค่า `DJANGO_SECRET_KEY` ใหม่ผ่าน environment variable (อย่าฝัง secret key ไว้ในโค้ด)
3. เปลี่ยนฐานข้อมูลจาก SQLite เป็น PostgreSQL/MySQL สำหรับการใช้งานจริง
4. รัน `python manage.py collectstatic` เพื่อรวบรวมไฟล์ static ก่อน deploy

---

## 📄 License
โปรเจกต์นี้จัดทำเพื่อการศึกษา (Educational Project)
