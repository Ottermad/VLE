from app import db
from app.exceptions import FieldInUseError, NotFoundError, UnauthorizedError,CustomError
from app.helper import json_from_request, check_keys, get_record_by_id
from app.lessons.models import Lesson, Subject
from app.user.helper_functions import get_user_by_id
from flask import jsonify
from flask.globals import g


def lesson_create(request):
    # Parse JSON from request
    data = json_from_request(request)

    # Check JSON has keys needed
    expected_keys = ['name', 'subject_id']
    check_keys(expected_keys=expected_keys, data=data)

    # Validate subject_id
    subject = get_record_by_id(
        data['subject_id'],
        Subject,
        custom_not_found_error=CustomError(409, message="Invalid subject_id.")
    )
    # Create lesson
    lesson = Lesson(
        name=data['name'],
        school_id=g.user.school_id,
        subject_id=subject.id
    )

    # Add teachers (if supplied)
    if 'teacher_ids' in data.keys():
        for teacher_id in data['teacher_ids']:
         user = get_user_by_id(
             teacher_id,
             custom_not_found_error=CustomError(
                 409, message="Invalid id in teacher_ids: {}".format(teacher_id))
         )
         # TODO: Add role checking
         lesson.teachers.append(user)

    # Add teachers (if supplied)
    if 'student_ids' in data.keys():
        for student_id in data['student_ids']:
            user = get_user_by_id(
                student_id,
                custom_not_found_error=CustomError(
                    409, message="Invalid id in student_ids: {}".format(student_id))
            )
            #  TODO: Add role checking
            lesson.students.append(user)

    db.session.add(lesson)
    db.session.commit()

    return jsonify({'success': True, 'lesson': lesson.to_dict(nest_teachers=True, nest_students=True)}), 201


def lesson_listing(request):
    # Get all lessons from school
    lessons = Lesson.query.filter_by(school_id=g.user.school_id)
    return jsonify({'success': True, 'lessons': [lesson.to_dict() for lesson in lessons]})


def lesson_detail(request, lesson_id):
    lesson = get_record_by_id(lesson_id, Lesson)
    return jsonify({'success': True, 'lesson': lesson.to_dict()})
