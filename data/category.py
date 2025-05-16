import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .db_session import SqlAchemyBase

class Category(SqlAchemyBase):
    __tablename__ = 'categories'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100), nullable=False)

    # Опционально: связь с задачами
    tasks = relationship('Task', back_populates='category')