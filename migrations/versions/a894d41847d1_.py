"""empty message

Revision ID: a894d41847d1
Revises: 
Create Date: 2024-10-20 18:52:05.478313

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a894d41847d1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("surname", sa.String(), nullable=False),
        sa.Column("registered_at", sa.DateTime(), nullable=False),
        sa.Column("telegraim_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(length=1000), nullable=False),
        sa.Column("date_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipient_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("messages")
    op.drop_table("users")
    # ### end Alembic commands ###
