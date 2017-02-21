"""Essay Functions."""
import datetime

from flask import g, jsonify

from app import db
from app.exceptions import UnauthorizedError, CustomError
from app.helper import json_from_request, check_keys, get_record_by_id
from app.homework.models import Essay, HomeworkType, Question, QuizAnswer, QuizSubmission, EssaySubmission
from app.lessons.models import Lesson


def create_essay(request):
    top_level_expected_keys = [
        "lesson_id",
        "title",
        "description",
        "date_due",
    ]
    json_data = json_from_request(request)
    check_keys(top_level_expected_keys, json_data)

    # Validate lesson
    lesson = get_record_by_id(json_data['lesson_id'], Lesson)
    if g.user.id not in [t.id for t in lesson.teachers]:
        raise UnauthorizedError()


    # Validate date
    date_due_string = json_data['date_due']
    try:
        date_due = datetime.datetime.strptime(date_due_string, "%d/%m/%Y").date()
    except ValueError:
        raise CustomError(409, message="Invalid date_due: {}.".format(json_data['date_due']))

    essay = Essay(
        lesson_id=json_data['lesson_id'],
        title=json_data['title'],
        description=json_data['description'],
        date_due=date_due,
    )

    db.session.add(essay)
    db.session.commit()

    return jsonify(essay.to_dict()), 201


def submit_essay(request, essay_id):
    # Check essay if valid
    essay = get_record_by_id(essay_id, Essay, check_school_id=False)
    if essay.lesson.school_id != g.user.school_id:
        raise UnauthorizedError()

    top_level_expected_keys = [
        "content"
    ]
    json_data = json_from_request(request)
    check_keys(top_level_expected_keys, json_data)

    #  Validate lesson
    lesson = get_record_by_id(essay.lesson.id, Lesson)
    if g.user.id not in [t.id for t in lesson.students]:
        raise UnauthorizedError()

    submission = EssaySubmission(
        essay.id,
        g.user.id,
        datetime.datetime.now(),  #  TODO: Deal with timezones
        json_data['content']
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({'success': True}), 201


def essay_detail(request, essay_id):
    # Check essay if valid
    essay = get_record_by_id(essay_id, Essay, check_school_id=False)
    if essay.lesson.school_id != g.user.school_id:
        raise UnauthorizedError()

    return jsonify({'success': True, 'essay': essay.to_dict()})
