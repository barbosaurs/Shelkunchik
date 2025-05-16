from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from data.db_session import SqlAchemyBase
from flask_login import UserMixin

class User(SqlAchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    solved_tasks = Column(Integer, default=0)

    tasks = relationship("UserTask", back_populates="user")
