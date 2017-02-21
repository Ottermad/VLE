from app import db
from app.exceptions import FieldInUseError, NotFoundError, UnauthorizedError,CustomError
from app.helper import json_from_request, check_keys, get_record_by_id, get_boolean_query_param
from app.lessons.models import Lesson, Subject
from flask import jsonify
from flask.globals import g
from .helper_functions import add_students, add_teachers


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

    # Validate name
    validate_lesson_name(data['name'], g.user.school_id)

    # Create lesson
    lesson = Lesson(
        name=data['name'],
        school_id=g.user.school_id,
        subject_id=subject.id
    )


    # Add teachers (if supplied)
    if 'teacher_ids' in data.keys():
        add_teachers(data['teacher_ids'], lesson)

    # Add students (if supplied)
    if 'student_ids' in data.keys():
        add_students(data['student_ids'], lesson)

    db.session.add(lesson)
    db.session.commit()

    return jsonify({'success': True, 'lesson': lesson.to_dict(nest_teachers=True, nest_students=True)}), 201


def validate_lesson_name(name, school_id):
    query = Lesson.query.filter_by(name=name, school_id=school_id)
    lesson = query.first()

    if lesson is not None:
        raise FieldInUseError('name')


def lesson_listing(request):
    # Get all lessons from school
    lessons = Lesson.query.filter_by(school_id=g.user.school_id)
    return jsonify({'success': True, 'lessons': [lesson.to_dict() for lesson in lessons]})


def lesson_detail(request, lesson_id):
    lesson = get_record_by_id(lesson_id, Lesson)
    nest_teachers = get_boolean_query_param(request, 'nest-teachers')
    nest_students = get_boolean_query_param(request, 'nest-students')
    nest_subject = get_boolean_query_param(request, 'nest-subject')
    nest_homework = get_boolean_query_param(request, 'nest-homework')
    return jsonify({'success': True, 'lesson': lesson.to_dict(nest_homework=nest_homework, nest_teachers=nest_teachers, nest_students=nest_students, nest_subject=nest_subject)})


def lesson_delete(request, lesson_id):
    lesson = get_record_by_id(lesson_id, Lesson)
    db.session.delete(lesson)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Deleted.'})


def lesson_update(request, lesson_id):
    lesson = get_record_by_id(lesson_id, Lesson)

    json_data = json_from_request(request)

    if "name" in json_data.keys():
        validate_lesson_name(name=json_data['name'], school_id=g.user.school_id)
        lesson.name = json_data['name']

    if "subject_id" in json_data.keys():
        subject = get_record_by_id(
            json_data['subject_id'],
            Subject,
            custom_not_found_error=CustomError(409, message="Invalid subject_id.")
        )
        lesson.subject_id = subject.id

    if "teacher_ids" in json_data.keys():
        lesson.teachers = []
        add_teachers(json_data['teacher_ids'], lesson)

    if "student_ids" in json_data.keys():
        lesson.students = []
        add_students(json_data['student_ids'], lesson)

    db.session.add(lesson)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Updated.'})


def lessons_taught(request):
    nest_teachers = get_boolean_query_param(request, 'nest-teachers')
    nest_students = get_boolean_query_param(request, 'nest-students')
    nest_subject = get_boolean_query_param(request, 'nest-subject')
    lessons = [lesson.to_dict(nest_teachers=nest_teachers, nest_students=nest_students, nest_subject=nest_subject) for lesson in g.user.lessons_taught]
    return jsonify({'success': True, 'lessons': lessons})
