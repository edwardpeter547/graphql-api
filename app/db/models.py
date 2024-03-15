import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Employer(Base):
    __tablename__ = "tb_employers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String)
    industry = Column(String)
    jobs = relationship("Job", back_populates="employer", lazy="joined")


class Job(Base):
    __tablename__ = "tb_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    employer_id = Column(Integer, ForeignKey("tb_employers.id"))
    employer = relationship("Employer", back_populates="jobs", lazy="joined")


class User(Base):
    __tablename__ = "tb_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    email = Column(String)
    password_hash = Column(String)
    role = Column(String)
    application = relationship("JobApplication", back_populates="user", lazy="joined")


class JobApplication(Base):
    __tablename__ = "tb_jobapplications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reference = Column(String)
    date = Column(DateTime, default=datetime.datetime.now())
    job_id = Column(Integer, ForeignKey("tb_jobs.id"))
    user_id = Column(Integer, ForeignKey("tb_users.id"))
    user = relationship("User", back_populates="application", lazy="joined")
