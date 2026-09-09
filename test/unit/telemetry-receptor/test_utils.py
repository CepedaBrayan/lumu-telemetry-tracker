from datetime import datetime, timezone

import pytest
from utils import parse_timestamp

# ---------------------------------------------------------------------------
# Documented use cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "2021-12-03T16:15:30.235Z",
            datetime(2021, 12, 3, 16, 15, 30, 235000, tzinfo=timezone.utc),
        ),
        (
            "2021-12-03T16:15:30.235",
            datetime(2021, 12, 3, 16, 15, 30, 235000, tzinfo=timezone.utc),
        ),
        (
            "2021-10-28T00:00:00.000",
            datetime(2021, 10, 28, tzinfo=timezone.utc),
        ),
        (
            "2011-12-03T10:15:30",
            datetime(2011, 12, 3, 10, 15, 30, tzinfo=timezone.utc),
        ),
        (
            1726668850124,
            datetime(2024, 9, 18, 14, 14, 10, 124000, tzinfo=timezone.utc),
        ),
        (
            "1726668850124",
            datetime(2024, 9, 18, 14, 14, 10, 124000, tzinfo=timezone.utc),
        ),
        (
            1726667942,
            datetime(2024, 9, 18, 13, 59, 2, tzinfo=timezone.utc),
        ),
        (
            "1726667942",
            datetime(2024, 9, 18, 13, 59, 2, tzinfo=timezone.utc),
        ),
        (
            969286895000,
            datetime(2000, 9, 18, 14, 21, 35, tzinfo=timezone.utc),
        ),
        (
            "969286895000",
            datetime(2000, 9, 18, 14, 21, 35, tzinfo=timezone.utc),
        ),
        (
            3336042095,
            datetime(2075, 9, 18, 14, 21, 35, tzinfo=timezone.utc),
        ),
        (
            "3336042095",
            datetime(2075, 9, 18, 14, 21, 35, tzinfo=timezone.utc),
        ),
        (
            3336042095000,
            datetime(2075, 9, 18, 14, 21, 35, tzinfo=timezone.utc),
        ),
        (
            "3336042095000",
            datetime(2075, 9, 18, 14, 21, 35, tzinfo=timezone.utc),
        ),
        (
            "2021-12-03 16:15:30",
            datetime(2021, 12, 3, 16, 15, 30, tzinfo=timezone.utc),
        ),
    ],
)
def test_parse_timestamp_accepts_documented_formats(value, expected):
    result = parse_timestamp(value)

    print(f"\nInput:    {value!r}")
    print(f"Expected: {expected.isoformat()}")
    print(f"Result:   {result.isoformat()}")

    assert result == expected


# ---------------------------------------------------------------------------
# Non-documented use cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            0,
            datetime(1970, 1, 1, tzinfo=timezone.utc),
        ),
        (
            "0",
            datetime(1970, 1, 1, tzinfo=timezone.utc),
        ),
        (
            -1,
            datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        ),
        (
            "-1",
            datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        ),
        (
            1000.5,
            datetime(1970, 1, 1, 0, 16, 40, 500000, tzinfo=timezone.utc),
        ),
        (
            "1000.5",
            datetime(1970, 1, 1, 0, 16, 40, 500000, tzinfo=timezone.utc),
        ),
        (
            946684800,
            datetime(2000, 1, 1, tzinfo=timezone.utc),
        ),
        (
            946684800000,
            datetime(2000, 1, 1, tzinfo=timezone.utc),
        ),
        (
            "946684800000",
            datetime(2000, 1, 1, tzinfo=timezone.utc),
        ),
        (
            "  1726667942  ",
            datetime(2024, 9, 18, 13, 59, 2, tzinfo=timezone.utc),
        ),
        (
            "2021-12-03T11:15:30-05:00",
            datetime(2021, 12, 3, 16, 15, 30, tzinfo=timezone.utc),
        ),
        (
            "2021-12-03T18:15:30+02:00",
            datetime(2021, 12, 3, 16, 15, 30, tzinfo=timezone.utc),
        ),
        (
            "2021-12-03T16:15:30+00:00",
            datetime(2021, 12, 3, 16, 15, 30, tzinfo=timezone.utc),
        ),
        (
            "2021-12-03T16:15:30.123456Z",
            datetime(
                2021,
                12,
                3,
                16,
                15,
                30,
                123456,
                tzinfo=timezone.utc,
            ),
        ),
    ],
)
def test_parse_timestamp_accepts_non_documented_formats(value, expected):
    result = parse_timestamp(value)

    print(f"\nInput:    {value!r}")
    print(f"Expected: {expected.isoformat()}")
    print(f"Result:   {result.isoformat()}")

    assert result == expected


# ---------------------------------------------------------------------------
# Non-documented use cases: unsupported types
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        None,
        [],
        {},
        (),
    ],
)
def test_parse_timestamp_rejects_unsupported_types(value):
    print(f"\nUnsupported input: {value!r}")
    print("Expected error: Unsupported timestamp type")

    with pytest.raises(
        ValueError,
        match="Unsupported timestamp type",
    ) as captured_error:
        parse_timestamp(value)

    print(f"Result error:   {captured_error.value}")


# ---------------------------------------------------------------------------
# Non-documented use cases: unexpected timestamp formats
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "",
        "not-a-timestamp",
        "2021/12/03 16:15:30",
        "03-12-2021 16:15:30",
        "December 3, 2021",
        "2021-12-03",
        "16:15:30",
        "yesterday",
        "1726667942abc",
        "abc1726667942",
        "2021-12-03T16:15",
        "2021-12-03T16:15:30 UTC",
        "NaN",
        "Infinity",
        "-Infinity",
    ],
)
def test_parse_timestamp_rejects_unexpected_formats(value):
    print(f"\nUnexpected input: {value!r}")
    print("Expected error: Unsupported timestamp format")

    with pytest.raises(
        ValueError,
        match="Unsupported timestamp format",
    ) as captured_error:
        parse_timestamp(value)

    print(f"Result error:   {captured_error.value}")


# ---------------------------------------------------------------------------
# Non-documented use cases: invalid calendar values
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "2021-13-03T16:15:30",
        "2021-00-03T16:15:30",
        "2021-12-32T16:15:30",
        "2021-02-29T16:15:30",
        "2021-12-03T25:15:30",
        "2021-12-03T16:60:30",
        "2021-12-03T16:15:60",
    ],
)
def test_parse_timestamp_rejects_invalid_calendar_values(value):
    print(f"\nInvalid calendar input: {value!r}")
    print("Expected: ValueError")

    with pytest.raises(ValueError) as captured_error:
        parse_timestamp(value)

    print(f"Result error: {captured_error.value}")


# ---------------------------------------------------------------------------
# Non-documented use cases: non-finite numeric timestamps
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_parse_timestamp_rejects_non_finite_numbers(value):
    print(f"\nNon-finite input: {value!r}")
    print("Expected error: Timestamp must be finite")

    with pytest.raises(
        ValueError,
        match="Timestamp must be finite",
    ) as captured_error:
        parse_timestamp(value)

    print(f"Result error:   {captured_error.value}")
