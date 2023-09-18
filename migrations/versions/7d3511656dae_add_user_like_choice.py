"""Add user like choice

Revision ID: 7d3511656dae
Revises: c62dad25140c
Create Date: 2023-09-09 19:41:44.758544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d3511656dae'
down_revision = 'c62dad25140c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_like',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('liked_user_id', sa.Uuid(), nullable=False),
    sa.Column('is_liked', sa.Boolean(), nullable=False),
    sa.CheckConstraint('NOT(user_id = liked_user_id)', name='_user_like_cc'),
    sa.ForeignKeyConstraint(['liked_user_id'], ['auth_user.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'liked_user_id', name='_user_like_uc')
    )
    op.create_unique_constraint('_match_uc', 'match', ['user1_id', 'user2_id'])
    op.drop_constraint('match_user1_id_fkey', 'match', type_='foreignkey')
    op.drop_constraint('match_user2_id_fkey', 'match', type_='foreignkey')
    op.create_foreign_key(None, 'match', 'auth_user', ['user2_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'match', 'auth_user', ['user1_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'match', type_='foreignkey')
    op.drop_constraint(None, 'match', type_='foreignkey')
    op.create_foreign_key('match_user2_id_fkey', 'match', 'auth_user', ['user2_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key('match_user1_id_fkey', 'match', 'auth_user', ['user1_id'], ['id'], ondelete='RESTRICT')
    op.drop_constraint('_match_uc', 'match', type_='unique')
    op.drop_table('user_like')
    # ### end Alembic commands ###
