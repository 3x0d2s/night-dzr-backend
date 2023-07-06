"""Add Game Table

Revision ID: f6c6f95c2cc7
Revises: 56a4ce26e01f
Create Date: 2023-07-05 16:40:20.125851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6c6f95c2cc7'
down_revision = '56a4ce26e01f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('legend', sa.String(), nullable=False),
    sa.Column('datetime_start', sa.DateTime(), nullable=False),
    sa.Column('datetime_end', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Game_id'), 'Game', ['id'], unique=False)
    op.create_table('GamesTasks',
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['Game.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['Task.id'], )
    )
    op.create_table('GamesTeams',
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['Game.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['Team.id'], )
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('GamesTeams')
    op.drop_table('GamesTasks')
    op.drop_index(op.f('ix_Game_id'), table_name='Game')
    op.drop_table('Game')
    # ### end Alembic commands ###
