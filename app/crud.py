# app/crud.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, auth, schemas
import secrets, string


# --- STUDENTS ---
def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()


def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def update_student(db: Session, student_id: int, student: schemas.StudentCreate):
    db_student = get_student(db, student_id)
    if not db_student:
        raise Exception("Student not found")
    for key, value in student.dict().items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int):
    db_student = get_student(db, student_id)
    if not db_student:
        raise Exception("Student not found")
    db.delete(db_student)
    db.commit()
    return {"ok": True}


# --- CLASSES ---
def create_class(db: Session, _class: schemas.ClassCreate):
    db_class = models.Class(**_class.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


def get_classes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Class).offset(skip).limit(limit).all()


def get_class(db: Session, class_id: int):
    return db.query(models.Class).filter(models.Class.id == class_id).first()


def update_class(db: Session, class_id: int, _class: schemas.ClassCreate):
    db_class = get_class(db, class_id)
    if not db_class:
        raise Exception("Class not found")
    for key, value in _class.dict().items():
        setattr(db_class, key, value)
    db.commit()
    db.refresh(db_class)
    return db_class


def delete_class(db: Session, class_id: int):
    db_class = get_class(db, class_id)
    if not db_class:
        raise Exception("Class not found")
    db.delete(db_class)
    db.commit()
    return {"ok": True}


# --- SUBJECTS ---
def create_subject(db: Session, subject: schemas.SubjectCreate):
    db_subject = models.Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def get_subjects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Subject).offset(skip).limit(limit).all()


def get_subject(db: Session, subject_id: int):
    return db.query(models.Subject).filter(models.Subject.id == subject_id).first()


def update_subject(db: Session, subject_id: int, subject: schemas.SubjectCreate):
    db_subject = get_subject(db, subject_id)
    if not db_subject:
        raise Exception("Subject not found")
    for key, value in subject.dict().items():
        setattr(db_subject, key, value)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def delete_subject(db: Session, subject_id: int):
    db_subject = get_subject(db, subject_id)
    if not db_subject:
        raise Exception("Subject not found")
    db.delete(db_subject)
    db.commit()
    return {"ok": True}


# --- RESULTS ---
def create_result(db: Session, result: schemas.ResultCreate):
    db_result = models.Result(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def get_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Result).offset(skip).limit(limit).all()


def get_result(db: Session, result_id: int):
    return db.query(models.Result).filter(models.Result.id == result_id).first()


def update_result(db: Session, result_id: int, result: schemas.ResultCreate):
    db_result = get_result(db, result_id)
    if not db_result:
        raise Exception("Result not found")

    # ✅ Only allow changing the score — nothing else!
    db_result.score = result.score

    db.commit()
    db.refresh(db_result)
    return db_result


def delete_result(db: Session, result_id: int):
    db_result = get_result(db, result_id)
    if not db_result:
        raise Exception("Result not found")
    db.delete(db_result)
    db.commit()
    return {"ok": True}


# --- TEACHERS ---
def create_teacher(db: Session, teacher_data: schemas.TeacherCreate):

    # 1. Generate random password
    password = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
    )

    # 2. Hash it
    password_hash = auth.hash_password(password)

    # 3. Create linked User
    db_user = models.User(
        email=teacher_data.email,
        password_hash=password_hash,
        role=models.RoleEnum.teacher,
        name=f"{teacher_data.first_name} {teacher_data.last_name}",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 4. Create teacher
    db_teacher = models.Teacher(
        first_name=teacher_data.first_name,
        last_name=teacher_data.last_name,
        user_id=db_user.id,
        contact=teacher_data.contact,
        status=teacher_data.status,
        specialization=teacher_data.specialization,
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)

    # 4️⃣ If `class_teacher_for` is given, update the class to link
    if teacher_data.class_teacher_for:
        class_ = db.query(models.Class).get(teacher_data.class_teacher_for)
        if class_:
            class_.class_teacher_id = db_teacher.id
            db.add(class_)
            db.commit()

    # 5️⃣ For each assignment, create links
    for assignment in teacher_data.assignments or []:
        for subject_id in assignment.subject_ids:
            link = models.ClassSubjectTeacher(
                class_id=assignment.class_id,
                subject_id=subject_id,
                teacher_id=db_teacher.id,
            )
            db.add(link)
    db.commit()

    # 6. Return teacher + plain password so admin can copy
    return {
        "teacher": {
            "id": db_teacher.id,
            "name": f"{db_teacher.first_name} {db_teacher.last_name}",
            "email": db_user.email,
        },
        "plain_password": password,
    }


def get_teachers(db: Session, skip: int = 0, limit: int = 100):
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()

    results = []
    for teacher in teachers:
        user = db.query(models.User).filter(models.User.id == teacher.user_id).first()

        results.append(
            {
                "id": teacher.id,
                "name": f"{teacher.first_name} {teacher.last_name}",
                "subjects": [],  # You can replace with real subject data later
                "classes": [],  # You can replace with real class data later
                "contact": user.email if user else "",
                "status": "Active",  # Replace with real status if you have a status field
            }
        )

    return results


def get_teacher(db: Session, teacher_id: int):
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()


def update_teacher(db: Session, teacher_id: int, teacher: schemas.TeacherCreate):
    db_teacher = get_teacher(db, teacher_id)
    if not db_teacher:
        raise Exception("Teacher not found")
    for key, value in teacher.dict().items():
        setattr(db_teacher, key, value)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


def delete_teacher(db: Session, teacher_id: int):
    db_teacher = get_teacher(db, teacher_id)
    if not db_teacher:
        raise Exception("Teacher not found")
    db.delete(db_teacher)
    db.commit()
    return {"ok": True}


# --- YEARS ---
def create_year(db: Session, year: schemas.YearCreate):
    db_year = models.Year(**year.dict())
    db.add(db_year)
    db.commit()
    db.refresh(db_year)
    return db_year


def get_years(db: Session):
    return db.query(models.Year).all()


# --- ClassSubjectTeacher ---
def create_class_subject_teacher(db: Session, link: schemas.ClassSubjectTeacherCreate):
    db_link = models.ClassSubjectTeacher(**link.dict())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


def get_class_subject_teacher(db: Session, link_id: int):
    return (
        db.query(models.ClassSubjectTeacher)
        .filter(models.ClassSubjectTeacher.id == link_id)
        .first()
    )


def get_class_subject_teachers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ClassSubjectTeacher).offset(skip).limit(limit).all()


def delete_class_subject_teacher(db: Session, link_id: int):
    link = get_class_subject_teacher(db, link_id)
    if not link:
        raise Exception("Not found")
    db.delete(link)
    db.commit()
    return {"ok": True}


# --- Users ---
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = user_update.name
    db.commit()
    db.refresh(user)
    return user
