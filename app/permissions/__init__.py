from flask import Blueprint, jsonify, g
from flask_jwt import jwt_required, current_identity

from app.exceptions import CustomError

from .models import Permission, Role, role_permissions, db

permissions_blueprint = Blueprint('permissions', __name__, url_prefix='/permissions')


@permissions_blueprint.route('/set-defaults/<int:school_id>', methods=["POST"])
@jwt_required()
def default(school_id):
    """
    Create default roles and permissions for school.

    Uses the currently logged in user as the initial admin.
    Only works if permissions do not exist yet.
    """

    # Check permissions not created yet.
    school_id = current_identity['school_id']
    if Permission.query.filter_by(school_id=school_id).first() is not None:
        raise CustomError(401, message='Permissions already setup.')

    # Create permissions
    for permission in Permission.default_permissions(school_id):
        db.session.add(permission)
    db.session.commit()

    # Create roles
    for role in Role.default_roles(school_id):
        db.session.add(role)
    db.session.commit()

    # Assign user to admin role
    role = Role.query.filter_by(name="ADMINISTRATOR", school_id=school_id).first()
    g.user.roles.append(role)
    db.session.add(g.user)
    db.session.commit()

    # Return success status
    return jsonify({'success': True})
