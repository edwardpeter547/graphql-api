from graphene import ObjectType, Int, String, List, Field, DateTime
from app.db.dataset import job_data, employer_data


class EmployerObject(ObjectType):
    id = Int()
    name = String()
    email = String()
    industry = String()
    jobs = List(lambda: JobObject)

    @staticmethod
    def resolve_jobs(root, info):
        return root.jobs


class JobObject(ObjectType):
    id = Int()
    title = String()
    description = String()
    employer_id = Int()
    employer = Field(EmployerObject)

    @staticmethod
    def resolve_employer(root, info):
        return root.employer


class UserObject(ObjectType):
    id = Int()
    username = String()
    email = String()
    role = String()
    applications = List(lambda: JobApplicationObject)

    @staticmethod
    def resolve_applications(root, info):
        return root.application


class JobApplicationObject(ObjectType):
    id = Int()
    reference = String()
    date = DateTime()
    job_id = Int()
    user_id = Int()
    user = Field(UserObject)

    @staticmethod
    def resolve_user(root, info):
        return root.user
