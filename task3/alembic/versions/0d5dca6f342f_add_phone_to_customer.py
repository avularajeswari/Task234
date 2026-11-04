"""add phone to customer

Revision ID: 0d5dca6f342f
Revises: 31494938c0cd
Create Date: 2026-11-04 16:18:24.048685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d5dca6f342f'
down_revision: Union[str, Sequence[str], None] = '31494938c0cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
