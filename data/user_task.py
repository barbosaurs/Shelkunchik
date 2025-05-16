from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from data.db_session import SqlAchemyBase

class UserTask(SqlAchemyBase):
    __tablename__ = 'user_tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    is_correct = Column(Boolean, default=False)

    user = relationship("User", back_populates="tasks")
    task = relationship("Task")
