from app.exceptions import CustomError
from app.helper import get_record_by_id
from app.user.models import User


def add_teachers(teacher_ids, lesson):
    for teacher_id in teacher_ids:
        user = get_record_by_id(
            teacher_id,
            User,
            custom_not_found_error=CustomError(
                409, message="Invalid id in teacher_ids: {}".format(teacher_id))
        )
        #  TODO: Add role checking
        lesson.teachers.append(user)


def add_students(student_ids, lesson):
    for student_id in student_ids:
        user = get_record_by_id(
            student_id,
            User,
            custom_not_found_error=CustomError(
                409, message="Invalid id in student_ids: {}".format(student_id))
        )
        #  TODO: Add role checking
        lesson.students.append(user)
