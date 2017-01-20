"""Homework Functions."""
import datetime

from flask import g, jsonify

from app import db
from app.exceptions import UnauthorizedError, CustomError
from app.helper import json_from_request, check_keys, get_record_by_id
from app.homework.models import Quiz, HomeworkType, Question, QuizAnswer, QuizSubmission
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


def submit_quiz(request, quiz_id):
    # Check quiz is valid
    quiz = get_record_by_id(quiz_id, Quiz, check_school_id=False)
    if quiz.lesson.school_id != g.user.school_id:
        raise UnauthorizedError()

    question_ids = [question.id for question in quiz.questions]

    submission = QuizSubmission(
        homework_id=quiz.id,
        user_id=g.user.id,
        datetime_submitted=datetime.datetime.now()  # TODO: Deal with timezones
    )

    json_data = json_from_request(request)
    expected_top_keys = ['answers']
    expected_inner_keys = ['question_id', 'answer']

    check_keys(expected_top_keys, json_data)

    for answer in json_data['answers']:
        check_keys(expected_inner_keys, answer)
        question = get_record_by_id(answer['question_id'], Question, check_school_id=False)
        if question.id not in question_ids:
            raise UnauthorizedError()

        answer = QuizAnswer(answer['answer'], submission.id, question.id)
        submission.answers.append(answer)

    submission.mark()
    db.session.add(submission)
    db.session.commit()
    return jsonify({'score': submission.total_score})
