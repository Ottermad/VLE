"""Homework Functions."""
import datetime

from flask import g, jsonify

from app import db
from app.exceptions import UnauthorizedError, CustomError
from app.helper import json_from_request, check_keys, get_record_by_id
from app.homework.models import Quiz, HomeworkType, Question
from app.lessons.models import Lesson


def create_quiz(request):
    top_level_expected_keys = [
        "lesson_id",
        "title",
        "description",
        "type",
        "date_due",
        "number_of_questions",
        "questions"
    ]
    json_data = json_from_request(request)
    check_keys(top_level_expected_keys, json_data)

    # Validate lesson
    lesson = get_record_by_id(json_data['lesson_id'], Lesson)
    if g.user.id not in [t.id for t in lesson.teachers]:
        raise UnauthorizedError()

    type_id = HomeworkType.HOMEWORK.value

    # Validate date
    date_due_string = json_data['date_due']
    try:
        date_due = datetime.datetime.strptime(date_due_string, "%d/%m/%Y").date()
    except ValueError:
        raise CustomError(409, message="Invalid date_due: {}.".format(json_data['date_due']))

    quiz = Quiz(
        lesson_id=json_data['lesson_id'],
        title=json_data['title'],
        description=json_data['description'],
        type_id=type_id,
        date_due=date_due,
        number_of_questions=json_data['number_of_questions']
    )

    db.session.add(quiz)
    db.session.commit()

    for question_object in json_data['questions']:
        if 'answer' and 'question_text' not in question_object.keys():
            raise CustomError(
                409,
                message="Invalid object in questions array. Make sure it has a question and a answer."
            )
        question = Question(quiz.id, question_object['question_text'], question_object['answer'])
        db.session.add(question)
        quiz.questions.append(question)

    db.session.add(quiz)
    db.session.commit()
    return jsonify(quiz.to_dict()), 201
