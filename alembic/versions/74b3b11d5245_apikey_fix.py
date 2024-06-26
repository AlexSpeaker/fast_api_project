"""ApiKey fix

Revision ID: 74b3b11d5245
Revises: 67fa25ffc7e5
Create Date: 2024-05-06 19:11:55.759016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74b3b11d5245'
down_revision: Union[str, None] = '67fa25ffc7e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('api_key_user_id_fkey', 'api_key', type_='foreignkey')
    op.create_foreign_key(None, 'api_key', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'api_key', type_='foreignkey')
    op.create_foreign_key('api_key_user_id_fkey', 'api_key', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###
