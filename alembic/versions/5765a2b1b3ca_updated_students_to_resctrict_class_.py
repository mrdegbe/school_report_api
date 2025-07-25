"""Updated students to resctrict class ondelete

Revision ID: 5765a2b1b3ca
Revises: afb8ca58ef64
Create Date: 2025-07-23 10:41:24.314836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5765a2b1b3ca'
down_revision: Union[str, Sequence[str], None] = 'afb8ca58ef64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_index('unique_active_academic_year', table_name='academic_years', postgresql_where='(is_active = true)')
    op.drop_constraint('students_class_id_fkey', 'students', type_='foreignkey')
    op.create_foreign_key(None, 'students', 'classes', ['class_id'], ['id'], ondelete='RESTRICT')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'students', type_='foreignkey')
    op.create_foreign_key('students_class_id_fkey', 'students', 'classes', ['class_id'], ['id'])
    op.create_index('unique_active_academic_year', 'academic_years', ['is_active'], unique=True, postgresql_where='(is_active = true)')
    # ### end Alembic commands ###
