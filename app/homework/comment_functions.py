from flask import g, jsonify
from app import db
from app.exceptions import UnauthorizedError
from app.helper import json_from_request, check_keys, get_record_by_id
from app.homework.models import Submission, Comment


def comment_create_view(request):
    top_level_expected_keys = [
        "submission_id",
        "text",
    ]

    json_data = json_from_request(request)
    check_keys(top_level_expected_keys, json_data)

    #  Validate submission
    submission = get_record_by_id(json_data['submission_id'], Submission, check_school_id=False)
    if g.user.id not in [t.id for t in submission.homework.lesson.teachers]:
        raise UnauthorizedError()

    comment = Comment(submission.id, json_data['text'], g.user.id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({"success": True, "comment": comment.to_dict()}), 201


def comment_detail_view(request, comment_id):
    comment = get_record_by_id(comment_id, Comment)
    return jsonify({'success': True, 'comment': comment.to_dict(nest_user=True)})


def comment_delete_view(request, comment_id):
    comment = get_record_by_id(comment_id, Comment)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted.'})


def comment_update_view(request, comment_id):
    # Get comment
    comment = get_record_by_id(comment_id, Comment)

    # Validate that user has permission
    if comment.user_id != g.user.id:
        raise UnauthorizedError()

    # Get JSON data
    data = json_from_request(request)

    # If name in data, then update the name
    if 'text' in data.keys():
        comment.name = data['text']

    db.session.add(comment)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Updated.'})