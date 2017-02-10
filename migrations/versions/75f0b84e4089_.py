"""empty message

Revision ID: 75f0b84e4089
Revises: 6d03a457be7c
Create Date: 2017-02-04 18:52:48.767155

"""

# revision identifiers, used by Alembic.
revision = '75f0b84e4089'
down_revision = '6d03a457be7c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('essay',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['homework.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('question', sa.Column('question_answer', sa.String(length=120), nullable=True))
    op.add_column('question', sa.Column('question_text', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('question', 'question_text')
    op.drop_column('question', 'question_answer')
    op.drop_table('essay')
    # ### end Alembic commands ###