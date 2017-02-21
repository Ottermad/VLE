"""empty message

Revision ID: 9db2b8105fd8
Revises: 92bfa22a2573
Create Date: 2017-02-21 09:59:10.362886

"""

# revision identifiers, used by Alembic.
revision = '9db2b8105fd8'
down_revision = '92bfa22a2573'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('form',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('school_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['school_id'], ['school.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('form_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'form', ['form_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'form_id')
    op.drop_table('form')
    ### end Alembic commands ###
