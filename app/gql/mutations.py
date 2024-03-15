import os
from graphene import Mutation, String, Int, Field, ObjectType, Boolean
from graphql import GraphQLError
from app.gql.types import JobObject, EmployerObject, UserObject
from app.db.models import Job, Employer, User, JobApplication
from app.db.database import Session
from app.settings.config import ADMIN_ROLES
from app.utils import (
    generate_token,
    verify_password,
    get_authenticated_user,
    hash_password,
    admin_user,
    is_authenticated,
    generate_reference,
)

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class AddJob(Mutation):
    class Arguments:
        title = String(required=True)
        description = String(required=True)
        employer_id = Int(required=True)

    job = Field(JobObject)

    @admin_user
    @staticmethod
    def mutate(root, info, title, description, employer_id):
        job = Job(title=title, description=description, employer_id=employer_id)
        with Session() as session:
            session.add(job)
            session.commit()
            session.refresh(job)
        return AddJob(job=job)


class UpdateJob(Mutation):
    class Arguments:
        job_id = Int(required=True)
        title = String()
        description = String()
        employer_id = Int()

    job = Field(JobObject)

    @admin_user
    @staticmethod
    def mutate(root, info, job_id, title=None, description=None, employer_id=None):
        session = Session()
        job = session.query(Job).filter(Job.id == job_id).first()

        if not job:
            raise Exception("Job not found")
        if title is not None:
            job.title = title
        if description is not None:
            job.description = description
        if employer_id is not None:
            job.employer_id = employer_id

        session.commit()
        session.refresh(job)
        session.close()
        return UpdateJob(job=job)


class DeleteJob(Mutation):
    class Arguments:
        id = Int(required=True)

    success = Boolean()

    @admin_user
    @staticmethod
    def mutate(root, info, id):
        session = Session()
        job = session.query(Job).filter(Job.id == id).first()
        if not job:
            raise Exception("Job not found")
        session.delete(job)
        session.commit()
        session.close()
        return DeleteJob(success=True)


class AddEmployer(Mutation):
    class Arguments:
        name = String(required=True)
        email = String(required=True)
        industry = String(required=True)

    employer = Field(EmployerObject)

    @admin_user
    @staticmethod
    def mutate(root, info, name, email, industry):

        employer = Employer(name=name, email=email, industry=industry)
        with Session() as session:
            session.add(employer)
            session.commit()
            session.refresh(employer)
        # main
        # return AddEmployer(employer=employer)
        return AddEmployer(employer=employer)


class UpdateEmployer(Mutation):
    class Arguments:
        id = Int(required=True)
        name = String()
        email = String()
        industry = String()

    employer = Field(EmployerObject)

    @admin_user
    @staticmethod
    def mutate(root, info, id, name=None, email=None, industry=None):
        session = Session()
        employer = session.query(Employer).filter(Employer.id == id).first()
        if not employer:
            raise Exception("Employer not found!")
        if name is not None:
            employer.name = name
        if email is not None:
            employer.email = email
        if industry is not None:
            employer.industry = industry
        session.commit()
        session.refresh(employer)
        session.close()
        return UpdateEmployer(employer=employer)


class DeleteEmployer(Mutation):
    class Arguments:
        id = Int(required=True)

    status = Boolean()

    @admin_user
    @staticmethod
    def mutate(root, info, id):
        session = Session()
        employee = session.query(Employer).filter(Employer.id == id).first()
        session.delete(employee)
        session.commit()
        session.close()
        return DeleteEmployer(status=True)


class LoginUser(Mutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    token = String()

    @staticmethod
    def mutate(root, info, email, password):
        session = Session()
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise GraphQLError("User with email does not exist")

        verify_password(user.password_hash, password=password)

        token = generate_token(email)
        return LoginUser(token=token)


class RegisterUser(Mutation):
    class Arguments:
        username = String(required=True)
        email = String(required=True)
        password = String(required=True)
        role = String(required=True)

    user = Field(UserObject)

    @staticmethod
    def mutate(root, info, username, email, password, role):
        # check if user with email is already registered.
        session = Session()
        authenticated_user = None

        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            raise GraphQLError(f"Account with email {email} already exist!")

        if role.lower() in ADMIN_ROLES:
            try:
                authenticated_user = get_authenticated_user(info.context)
            except Exception:
                raise GraphQLError(f"Must be authenticated to add {role} level users")

            if authenticated_user.role not in ADMIN_ROLES:
                raise GraphQLError(
                    f"Must be authenticated as admin to add {role} level users"
                )

        # register user.
        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            role=role.lower(),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()
        return RegisterUser(user=user)


class NewApplication(Mutation):
    class Arguments:
        job_id = Int(required=True)
        user_id = Int(required=True)

    message = String()

    @is_authenticated
    @staticmethod
    def mutate(root, info, job_id):
        user = get_authenticated_user(info.context)

        session = Session()
        existing_application = (
            session.query(JobApplication)
            .filter(JobApplication.job_id == job_id, JobApplication.user_id == user.id)
            .first()
        )
        if existing_application:
            raise GraphQLError("You already applied for this role!")

        application = JobApplication(
            reference=generate_reference(), job_id=job_id, user_id=user.id
        )
        session.add(application)
        session.commit()
        session.refresh(application)
        session.close()
        return NewApplication(
            message=f"Your application with reference {application.reference} has been submitted."
        )


class Mutations(ObjectType):
    add_job = AddJob.Field()
    update_job = UpdateJob.Field()
    delete_job = DeleteJob.Field()
    add_employer = AddEmployer.Field()
    update_employer = UpdateEmployer.Field()
    delete_employer = DeleteEmployer.Field()
    login_user = LoginUser.Field()
    register_user = RegisterUser.Field()
    job_application = NewApplication.Field()
