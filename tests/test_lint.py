""" Tests for sqlite_clean.lint """

from sqlite_clean.lint import (
    contains_conflicting_aff_storage_class,
    contains_str_like_null,
)


def test_contains_conflicting_aff_storage_class(
    database_engine_for_testing, err_database_engine_for_testing
):
    """
    Testing contains_conflicting_aff_storage_class
    """

    # test string-based sql_path and empty database (no schema should mean no conflict)
    assert contains_conflicting_aff_storage_class(sql_engine=":memory:") is False

    # test non-conflicting database
    assert (
        contains_conflicting_aff_storage_class(sql_engine=database_engine_for_testing)
        is False
    )
    # test non-conlicting database single table
    assert (
        contains_conflicting_aff_storage_class(
            sql_engine=database_engine_for_testing, table_name="tbl_a"
        )
        is False
    )
    # test non-conlicting database single table and single column
    assert (
        contains_conflicting_aff_storage_class(
            sql_engine=database_engine_for_testing,
            table_name="tbl_a",
            column_name="col_integer",
        )
        is False
    )

    # add a conflicting row of values for tbl_a
    with database_engine_for_testing.begin() as connection:
        connection.execute(
            """
            INSERT INTO tbl_a (col_integer, col_text, col_blob, col_real)
            VALUES ('nan', 'None', 'example', 0.5);
            """
        )

    # test conflicting database
    assert (
        contains_conflicting_aff_storage_class(sql_engine=database_engine_for_testing)
        is True
    )
    # test conflicting database single table, conflicting table
    assert (
        contains_conflicting_aff_storage_class(
            sql_engine=database_engine_for_testing, table_name="tbl_a"
        )
        is True
    )
    # test conflicting database single table, non-conflicting table
    assert (
        contains_conflicting_aff_storage_class(
            sql_engine=database_engine_for_testing, table_name="tbl_b"
        )
        is False
    )
    # test conflicting database single table and single conflicting column
    assert (
        contains_conflicting_aff_storage_class(
            sql_engine=database_engine_for_testing,
            table_name="tbl_a",
            column_name="col_integer",
        )
        is True
    )
    # test conflicting database single table and single non-conflicting column
    assert (
        contains_conflicting_aff_storage_class(
            sql_engine=database_engine_for_testing,
            table_name="tbl_a",
            column_name="col_text",
        )
        is False
    )

    # test passing non-existent column affinity type (unable to validated for storage classes)
    assert (
        contains_conflicting_aff_storage_class(
            sql_engine=err_database_engine_for_testing,
            table_name="tbl_a",
            column_name="col_nonexistent",
        )
        is False
    )


def test_contains_str_like_null(database_engine_for_testing):
    """
    Testing contains_str_like_null
    """

    # assert no strs like nulls in full database
    assert contains_str_like_null(database_engine_for_testing) is False

    # add a str like null
    with database_engine_for_testing.begin() as connection:
        connection.execute(
            """
            INSERT INTO tbl_a (col_integer, col_text, col_blob, col_real)
            VALUES ('NaN', 'NULL', 'nan', 'None');
            """
        )

    # assert strs like nulls in specific cols
    assert (
        contains_str_like_null(
            database_engine_for_testing, table_name="tbl_a", column_name="col_integer"
        )
        and contains_str_like_null(
            database_engine_for_testing, table_name="tbl_a", column_name="col_text"
        )
        and contains_str_like_null(
            database_engine_for_testing, table_name="tbl_a", column_name="col_blob"
        )
        and contains_str_like_null(
            database_engine_for_testing, table_name="tbl_a", column_name="col_real"
        )
    ) is True

    # assert no strs like nulls in specific table
    assert (
        contains_str_like_null(database_engine_for_testing, table_name="tbl_b") is False
    )
