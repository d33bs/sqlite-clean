"""
pytest conftest file for shared fixtures etc.
"""
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


# note: we use name here to avoid pylint flagging W0621
@pytest.fixture(name="get_tempdir")
def fixture_get_tempdir() -> str:
    """
    Provide temporary directory for testing
    """

    return tempfile.gettempdir()


@pytest.fixture
def database_engine_for_testing(get_tempdir: str) -> Engine:
    """
    A database engine for testing as a fixture to be passed
    to other tests within this file.
    """

    # create a temporary sqlite connection
    sql_path = f"sqlite:///{get_tempdir}/test_sqlite.sqlite"
    engine = create_engine(sql_path)

    # statements for creating database with simple structure
    create_stmts = [
        "drop table if exists tbl_a;",
        """
        create table tbl_a (
        col_integer INTEGER NOT NULL
        ,col_text TEXT
        ,col_blob BLOB
        ,col_real REAL
        );
        """,
        "drop table if exists tbl_b;",
        """
        create table tbl_b (
        col_integer INTEGER
        ,col_text TEXT
        ,col_blob BLOB
        ,col_real REAL
        );
        """,
    ]

    insert_vals = [1, "sample", b"sample_blob", 0.5]

    with engine.begin() as connection:
        for stmt in create_stmts:
            connection.execute(stmt)

        # insert statement with some simple values
        # note: we use SQLAlchemy's parameters to insert data properly, esp. BLOB
        connection.execute(
            (
                "INSERT INTO tbl_a (col_integer, col_text, col_blob, col_real)"
                "VALUES (?, ?, ?, ?);"
            ),
            insert_vals,
        )
        connection.execute(
            (
                "INSERT INTO tbl_b (col_integer, col_text, col_blob, col_real)"
                "VALUES (?, ?, ?, ?);"
            ),
            insert_vals,
        )

    return engine


@pytest.fixture
def err_database_engine_for_testing(get_tempdir: str) -> Engine:
    """
    An erroneous database engine for testing as a fixture to be passed
    to other tests within this file.
    """

    # create a temporary sqlite connection
    sql_path = f"sqlite:///{get_tempdir}/test_sqlite_err.sqlite"
    engine = create_engine(sql_path)

    # statements for creating database with simple structure
    create_stmts = [
        "drop table if exists tbl_a;",
        """
        create table tbl_a (
        col_nonexistent NONEXISTENT
        );
        """,
    ]

    insert_vals = [1]

    with engine.begin() as connection:
        for stmt in create_stmts:
            connection.execute(stmt)

        # insert statement with some simple values
        # note: we use SQLAlchemy's parameters to insert data properly, esp. BLOB
        connection.execute(
            "INSERT INTO tbl_a (col_nonexistent) VALUES (?);",
            insert_vals,
        )

    return engine
