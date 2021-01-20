import os
import sys

import psycopg2 as dbapi2

INIT_STATEMENTS = [
    """
    create table if not exists my_user(
        id serial primary key,
        password int not null,
        name varchar not null unique,
        country varchar not null,
        type varchar not null
    )
    """,
    """
    create table if not exists charity_person(
        id int not null unique,
        applictaion_id int,
        donated_patients int not null,
        balance integer default 0 not null,
        FOREIGN KEY (id) REFERENCES my_user (id)
    )
    """,
    """
    create table if not exists patient(
        charity_person_helped int not null,
        id int not null unique,
        disease_id int,
        FOREIGN KEY (id) REFERENCES my_user (id)
    )
    """,
    """
    create table if not exists application_for_charity(
        application_id serial primary key,
        amount_of_help int not null,
        title varchar not null,
        application_duration int not null,
        numof_charity_people int not null,
        date int not null,
        approved boolean default false not null,
        patient_id int not null,
        FOREIGN KEY (patient_id) REFERENCES  patient (id)
    )
    """,
    """
    create table if not exists disease(
        disease_id serial primary key,
        disease_name varchar not null
    )
    """,
    """
    create table if not exists disease_patient(
        patient_id integer references patient(id) on delete set null on update cascade,
        disease_id integer references disease(disease_id) on delete set null on update cascade,
        primary key(patient_id, disease_id)
    )
    """,
    """
    create table if not exists disease_application(
        application_id integer references application_for_charity(application_id) on delete set null on update cascade,
        disease_id integer references disease(disease_id) on delete set null on update cascade,
        primary key(application_id, disease_id)
    )
    """,
    """
    create table if not exists charity_application(
        charity_id integer references charity_person(id) on delete set null on update cascade,
        application_id integer references application_for_charity(application_id) on delete set null on update cascade,
        primary key(application_id, charity_id)
    )
    """
]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py")  # , file=sys.stderr)
        sys.exit(1)
    initialize(url)