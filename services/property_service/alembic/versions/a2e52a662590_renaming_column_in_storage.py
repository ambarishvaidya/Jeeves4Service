"""Renaming column in Storage.

Revision ID: a2e52a662590
Revises: 9397cb79870d
Create Date: 2025-07-31 18:55:44.336115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2e52a662590'
down_revision: Union[str, Sequence[str], None] = '9397cb79870d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        schema='property',
        table_name='storage',
        column_name='storage_id',
        new_column_name='container_id',         
        )    
    

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        schema='property',
        table_name='storage',
        column_name='container_id',
        new_column_name='storage_id',
    )
