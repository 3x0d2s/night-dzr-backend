"""Add Task table

Revision ID: 56a4ce26e01f
Revises: 4d56622eaa34
Create Date: 2023-06-17 14:30:41.128121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56a4ce26e01f'
down_revision = '4d56622eaa34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('mystery_of_place', sa.String(), nullable=False),
    sa.Column('place', sa.String(), nullable=False),
    sa.Column('answer', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Task_id'), 'Task', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_Task_id'), table_name='Task')
    op.drop_table('Task')
    # ### end Alembic commands ###
