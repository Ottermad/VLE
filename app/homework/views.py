from app.exceptions import UnauthorizedError
from app.helper import get_boolean_query_param, get_record_by_id
from app.homework.comment_functions import comment_create_view, comment_detail_view, comment_delete_view, \
    comment_update_view
from app.homework.essay_functions import create_essay, submit_essay, essay_detail
from app.homework.quiz_functions import create_quiz, submit_quiz, quiz_detail
from app.permissions.decorators import permissions_required
from flask import Blueprint, request, g, jsonify
from flask_jwt import jwt_required
from .models import *

homework_blueprint = Blueprint('homework', __name__, url_prefix='/homework')


@homework_blueprint.route('/')
def index():
    return "Homework Index"


@homework_blueprint.route('/submissions')
@jwt_required()
@permissions_required({'Student'})
def list_my_submissions():
    submissions = Submission.query.filter_by(user_id=g.user.id)
    submissions_list = [s.to_dict(nest_homework=True, nest_comments=True) for s in submissions]
    return jsonify({'success': True, 'submissions': submissions_list})


@homework_blueprint.route('/homework/<int:homework_id>/submissions')
@jwt_required()
@permissions_required({'Teacher'})
def list_submissions(homework_id):
    homework = get_record_by_id(homework_id, Homework, check_school_id=False)
    if homework.lesson.school_id != g.user.school_id:
        raise UnauthorizedError()
    submissions = Submission.query.filter_by(homework_id=homework.id).all()
    return jsonify({'success': True, 'submissions': [s.to_dict(nest_user=True) for s in submissions]})


@homework_blueprint.route('/due/<int:lesson_id>')
@jwt_required()
def homework_due_for_lesson(lesson_id):
    homework = Homework.query.filter(Homework.lesson_id == lesson_id)
    return jsonify({'success': True, 'homework': [h.to_dict(date_as_string=True) for h in homework]})


@homework_blueprint.route('/summary')
@jwt_required()
@permissions_required({"Student"})
def homework_due_summary():
    lesson_ids = [l.id for l in g.user.lessons_attending]
    homework = Homework.query.filter(Homework.lesson_id.in_(lesson_ids))
    nest_lessons = get_boolean_query_param(request, 'nest-lessons')
    homework_list = [h.to_dict(date_as_string=True, nest_lesson=nest_lessons, has_submitted=True, user_id=g.user.id) for h in homework]

    return jsonify({'success': True, 'homework': homework_list})


# Quiz Routes
@homework_blueprint.route('/quiz', methods=("POST", "GET"))
@jwt_required()
def quiz_get_or_create():
    if request.method == 'POST':
        if g.user.has_permissions({'Teacher'}):
            return create_quiz(request)


@homework_blueprint.route('/quiz/<int:quiz_id>', methods=("POST", "GET"))
@jwt_required()
@permissions_required({'Student'})
def quiz_submit(quiz_id):
    if request.method == "POST":
        return submit_quiz(request, quiz_id)
    return quiz_detail(request, quiz_id)


@homework_blueprint.route('/quiz/submission/<int:submission_id>')
@jwt_required()
def view_quiz_submission(submission_id):
    if not (g.user.has_permissions({'Teacher'}) or g.user.has_permissions({'Student'})):
        raise UnauthorizedError()

    submission = get_record_by_id(submission_id, QuizSubmission, check_school_id=False)
    if submission.homework.lesson.school_id != g.user.school_id:
        raise UnauthorizedError()

    return jsonify({'success': True, 'submission': submission.to_dict(nest_user=True, nest_homework=True, nest_comments=True)})


# Essay Routes
@homework_blueprint.route('/essay', methods=("POST",))
@jwt_required()
def essay_get_or_create():
    if request.method == 'POST':
        if g.user.has_permissions({'Teacher'}):
            return create_essay(request)


@homework_blueprint.route('/essay/<int:essay_id>', methods=("POST", "GET"))
@jwt_required()
def essay_submit(essay_id):
    if request.method == "POST":
        return submit_essay(request, essay_id)
    else:
        return essay_detail(request, essay_id)


@homework_blueprint.route('/essay/submission/<int:submission_id>')
@jwt_required()
def view_essay_submission(submission_id):
    if not (g.user.has_permissions({'Teacher'}) or g.user.has_permissions({'Student'})):
        raise UnauthorizedError()

    submission = get_record_by_id(submission_id, EssaySubmission, check_school_id=False)
    if submission.homework.lesson.school_id != g.user.school_id:
        raise UnauthorizedError()

    return jsonify({'success': True, 'submission': submission.to_dict(nest_user=True, nest_homework=True, nest_comments=True)})


# Comment Routes
@homework_blueprint.route("/comment", methods=("POST", "GET"))
@jwt_required()
@permissions_required({"Teacher"})
def comment_listing_or_creation():
    if request.method == "POST":
        return comment_create_view(request)


@homework_blueprint.route("/comment/<int:comment_id>", methods=("PUT", "DELETE", "GET"))
@jwt_required()
@permissions_required({"Teacher"})
def comment_detail(comment_id):
    if request.method == "DELETE":
        return comment_delete_view(request, comment_id)
    if request.method == "PUT":
        return comment_update_view(request, comment_id)
    if request.method == "GET":
        return comment_detail_view(request, comment_id)
