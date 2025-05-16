import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .db_session import SqlAchemyBase

class Task(SqlAchemyBase):
    __tablename__ = 'tasks'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String(200), nullable=False)
    description = sa.Column(sa.Text, nullable=False)
    correct_answer = sa.Column(sa.String(200), nullable=False)
    solution = sa.Column(sa.Text, nullable=False)
    category_id = sa.Column(sa.Integer, sa.ForeignKey('categories.id'))
    category = relationship('Category', back_populates='tasks')