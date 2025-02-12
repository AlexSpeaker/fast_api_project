"""fix

Revision ID: c565eae589f4
Revises: 5c66673e875a
Create Date: 2025-02-12 23:56:34.560181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c565eae589f4'
down_revision: Union[str, None] = '5c66673e875a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('attachments_tweet_id_fkey', 'attachments', type_='foreignkey')
    op.create_foreign_key(None, 'attachments', 'tweets', ['tweet_id'], ['id'])
    op.drop_constraint('likes_tweet_id_fkey', 'likes', type_='foreignkey')
    op.drop_constraint('likes_user_id_fkey', 'likes', type_='foreignkey')
    op.create_foreign_key(None, 'likes', 'tweets', ['tweet_id'], ['id'])
    op.create_foreign_key(None, 'likes', 'users', ['user_id'], ['id'])
    op.drop_constraint('tweets_user_id_fkey', 'tweets', type_='foreignkey')
    op.create_foreign_key(None, 'tweets', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tweets', type_='foreignkey')
    op.create_foreign_key('tweets_user_id_fkey', 'tweets', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'likes', type_='foreignkey')
    op.drop_constraint(None, 'likes', type_='foreignkey')
    op.create_foreign_key('likes_user_id_fkey', 'likes', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('likes_tweet_id_fkey', 'likes', 'tweets', ['tweet_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'attachments', type_='foreignkey')
    op.create_foreign_key('attachments_tweet_id_fkey', 'attachments', 'tweets', ['tweet_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
