"""Add recovery codes

Revision ID: 28f2a91d7c44
Revises: 7cdb394fe8a7
Create Date: 2026-08-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "28f2a91d7c44"
down_revision: Union[str, Sequence[str], None] = "7cdb394fe8a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recovery_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hash_code", sa.String(length=255), nullable=False),
        sa.Column(
            "used",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recovery_codes_user_id"),
        "recovery_codes",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_recovery_codes_user_id"), table_name="recovery_codes")
    op.drop_table("recovery_codes")
