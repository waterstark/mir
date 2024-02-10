"""new_get_quest_rools

Revision ID: afd4c92e479a
Revises: 84f11c7d251e
Create Date: 2024-01-20 23:59:24.450554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afd4c92e479a'
down_revision = '5478d7d7a63f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_questionnaire', sa.Column('is_prem', sa.Boolean(), nullable=False))
    op.add_column('user_questionnaire', sa.Column('quest_lists_per_day', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_questionnaire', 'quest_lists_per_day')
    op.drop_column('user_questionnaire', 'is_prem')
    # ### end Alembic commands ###
