"""empty message

Revision ID: 1c06401d14d7
Revises: 75f0b84e4089
Create Date: 2017-02-15 14:04:35.461926

"""

# revision identifiers, used by Alembic.
revision = '1c06401d14d7'
down_revision = '75f0b84e4089'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('week',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('school_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['school_id'], ['school.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('period',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('week_id', sa.Integer(), nullable=True),
    sa.Column('day', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('end_time', sa.Time(), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['week_id'], ['week.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('timetabled_lesson',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('period_id', sa.Integer(), nullable=True),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lesson.id'], ),
    sa.ForeignKeyConstraint(['period_id'], ['period.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('timetabled_lesson')
    op.drop_table('period')
    op.drop_table('week')
    ### end Alembic commands ###