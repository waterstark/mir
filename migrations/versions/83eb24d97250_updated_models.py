"""Updated models

Revision ID: 83eb24d97250
Revises: d42f3150b232
Create Date: 2023-07-27 23:02:39.453716

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '83eb24d97250'
down_revision = 'd42f3150b232'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender', sa.Uuid(), nullable=False),
    sa.Column('receiver', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('message_text', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['receiver'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_id'), 'message', ['id'], unique=False)
    op.drop_index('ix_messages_id', table_name='messages')
    op.drop_table('messages')
    op.drop_constraint('like_user_id_fkey', 'like', type_='foreignkey')
    op.drop_constraint('like_liked_user_id_fkey', 'like', type_='foreignkey')
    op.create_foreign_key(None, 'like', 'user', ['liked_user_id'], ['id'])
    op.create_foreign_key(None, 'like', 'user', ['user_id'], ['id'])
    op.add_column('user', sa.Column('is_delete', sa.Boolean(), nullable=False))
    op.alter_column('user_questionnaire', 'gender',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('user_questionnaire', 'country',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('user_questionnaire', 'city',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('user_questionnaire', 'latitude',
               existing_type=sa.NUMERIC(precision=8, scale=5),
               nullable=True)
    op.alter_column('user_questionnaire', 'longitude',
               existing_type=sa.NUMERIC(precision=8, scale=5),
               nullable=True)
    op.alter_column('user_questionnaire', 'about',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('user_questionnaire', 'passion',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('user_questionnaire', 'height',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('user_questionnaire', 'goals',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('user_questionnaire', 'body_type',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_questionnaire', 'body_type',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('user_questionnaire', 'goals',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('user_questionnaire', 'height',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('user_questionnaire', 'passion',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('user_questionnaire', 'about',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('user_questionnaire', 'longitude',
               existing_type=sa.NUMERIC(precision=8, scale=5),
               nullable=False)
    op.alter_column('user_questionnaire', 'latitude',
               existing_type=sa.NUMERIC(precision=8, scale=5),
               nullable=False)
    op.alter_column('user_questionnaire', 'city',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('user_questionnaire', 'country',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('user_questionnaire', 'gender',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.drop_column('user', 'is_delete')
    op.drop_constraint(None, 'like', type_='foreignkey')
    op.drop_constraint(None, 'like', type_='foreignkey')
    op.create_foreign_key('like_liked_user_id_fkey', 'like', 'user', ['liked_user_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key('like_user_id_fkey', 'like', 'user', ['user_id'], ['id'], ondelete='RESTRICT')
    op.create_table('messages',
    sa.Column('sender', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('receiver', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('message_text', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['receiver'], ['user.id'], name='messages_receiver_fkey', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['sender'], ['user.id'], name='messages_sender_fkey', ondelete='RESTRICT')
    )
    op.create_index('ix_messages_id', 'messages', ['id'], unique=False)
    op.drop_index(op.f('ix_message_id'), table_name='message')
    op.drop_table('message')
    # ### end Alembic commands ###
