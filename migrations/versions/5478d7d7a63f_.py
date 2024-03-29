"""empty message

Revision ID: 5478d7d7a63f
Revises: 84f11c7d251e
Create Date: 2024-02-04 14:54:29.320829

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5478d7d7a63f'
down_revision = 'aa83adadcdb2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('message', sa.Column('reply_to', sa.Uuid(), nullable=True))
    op.add_column('message', sa.Column('group_id', sa.Uuid(), nullable=True))
    op.add_column('message', sa.Column('media', sa.String(), nullable=True))
    op.create_foreign_key(None, 'message', 'message', ['reply_to'], ['id'], ondelete='SET NULL')
    op.drop_column('message', 'captions')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('captions', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'message', type_='foreignkey')
    op.drop_column('message', 'media')
    op.drop_column('message', 'group_id')
    op.drop_column('message', 'reply_to')
    op.drop_column('message', 'created_at')
    # ### end Alembic commands ###
