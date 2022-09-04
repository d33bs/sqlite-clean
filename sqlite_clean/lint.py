"""
sqlite-clean linting - Detecting and alerting possible data challenges within SQlite.
"""

import logging
from typing import Optional, Tuple, Union

from sqlalchemy.engine.base import Engine

from sqlite_clean.constants import LIKE_NULLS, SQLITE_AFF_REF
from sqlite_clean.utils import collect_columns, engine_from_str

logger = logging.getLogger(__name__)

# pylint: disable=unused-argument


def contains_conflicting_aff_storage_class(
    *args,
    sql_engine: Union[str, Engine],
    table_name: Optional[str] = None,
    column_name: Optional[str] = None,
    **kwargs,
) -> bool:
    """
    Detect conflicting column affinity vs data storage class for
    entire SQLite database, a specific table, or a specific column
    within a specific table. See the following for more details on
    affinity vs storage class typing within SQLite:
    https://www.sqlite.org/datatype3.html

    Parameters
    ----------
    sql_engine: str | sqlalchemy.engine.base.Engine
        filename of the SQLite database or existing sqlalchemy engine
    table_name: str
        optional specific table name to check within database, by default None
    column_name: str
        optional specific column name to check within database, by default None

    Returns
    -------
    bool
        Returns True if conflicting storage class values were detected
        in database provided, else returns False.
    """

    logger.info(
        (
            "Determining if SQLite database contains conflicting column "
            "affinity vs storage class values."
        )
    )

    # create an engine
    engine = engine_from_str(sql_engine)

    # Gather columns to be used below.
    # Data returned is similar to the following
    # and may be accessed using index or key name.
    # [('table_name', 'column_name', 'column_type', 'notnull'),...]
    columns = collect_columns(engine, table_name, column_name)

    with engine.connect() as connection:
        for col in columns:

            if col["column_type"] in SQLITE_AFF_REF:
                root_coltype = col["column_type"]
            elif col["column_type"] in [
                item for chunk in SQLITE_AFF_REF.values() for item in chunk
            ]:
                root_coltype = list(
                    {
                        key: chunk
                        for key, chunk in SQLITE_AFF_REF.items()
                        for item in chunk
                        if item == col["column_type"]
                    }.keys()
                )[0]
            else:
                logger.warning(
                    "Unable to find related column affinity for column of type %s.",
                    col["column_type"],
                )
                continue

            # join formatted string for use with sql query in {col_types} var
            col_types = ",".join(
                [f"'{x.lower()}'" for x in SQLITE_AFF_REF[root_coltype]]
            )

            # there are challenges with using sqlalchemy vars in the same manner as above
            # so we use an f-string here along with nosec
            result = connection.execute(
                # the sql below seeks to efficiently detect existence of values which
                # do not match the column affinity type (for ex. a string in an integer column).
                f"""
                SELECT
                EXISTS(
                    SELECT 1 FROM {col["table_name"]}
                    WHERE TYPEOF({col["column_name"]}) NOT IN ({col_types})
                )
                AS 'CONFLICTING_TYPES_EXIST';
                """
            ).fetchone()[
                "CONFLICTING_TYPES_EXIST"
            ]  # nosec
            if result > 0:
                # if our result is greater than 0 it means values with conflicting storage
                # class existed within the focus column and as a result, we return False
                logger.warning(
                    "Discovered conflicting %s column %s affinity type and storage class.",
                    col["table_name"],
                    col["column_name"],
                )
                return True

    # return false if we did not find conflicting affinity vs storage class values
    logger.info(
        "Found no conflicting affinity vs storage class data within provided database."
    )

    return False


def contains_str_like_null(
    sql_engine: Union[str, Engine],
    table_name: Optional[str] = None,
    column_name: Optional[str] = None,
    like_nulls: Tuple[str, ...] = LIKE_NULLS,
) -> bool:
    """
    Detect whether the given database, table, or column contains
    a string value which is similar to NULL. Strings instead of
    SQLite NULL may be interpreted at read as a string (value)
    instead of a NULL (non-value).

    Parameters
    ----------
    sql_engine: str | sqlalchemy.engine.base.Engine
        filename of the SQLite database or existing sqlalchemy engine
    table_name: str
        optional specific table name to check within database, by default None
    column_name: str
        optional specific column name to check within database, by default None
    like_nulls: List[str]
        tuple strings which may represent null values, by default LIKE_NULLS global

    Returns
    -------
    bool
        Returns True if found a str value similar to null, else returns False.
    """

    logger.info(
        "Determining if SQLite database contains table entries with string values like NULL's."
    )

    # create an engine
    engine = engine_from_str(sql_engine)

    # gather columns to be used below
    columns = collect_columns(engine, table_name, column_name)

    # strings which are like nulls for later use in below SQL 'in'
    like_nulls_str_list = ",".join([f"'{x}'" for x in like_nulls])

    with engine.connect() as connection:
        for col in columns:
            # the sql below seeks to efficiently detect existence of string
            # values which are like nulls in columns which contain at least
            # one string value. Note that we must check the individual value
            # types instead of the column types due to SQLite's flexible
            # typing system.
            result = connection.execute(
                f"""
                SELECT
                (EXISTS(
                    SELECT 1 FROM {col["table_name"]}
                    WHERE TYPEOF({col["column_name"]}) = 'text'
                )
                AND EXISTS(
                    SELECT 1 FROM {col["table_name"]}
                    WHERE LOWER({col["column_name"]}) IN ({like_nulls_str_list})
                ))
                AS 'LIKE_NULL_EXISTS';
                """
            ).fetchone()[
                "LIKE_NULL_EXISTS"
            ]  # nosec
            if result > 0:
                # if our result is greater than 0 it means values with str's like null
                # existed within the focus column and as a result, we return False
                logger.warning(
                    "Discovered strings like nulls in %s column %s.",
                    col["table_name"],
                    col["column_name"],
                )
                return True

    return False
