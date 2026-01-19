import pytest
from decimal import Decimal
from DataModels.parkingLotsModel import ParkingLot
from DataAccesLayer import db_utils_parkingLots as parkingLot_utils

def dummy_row():
    return {
        "id": 676767,
        "name": "67",
        "location": "67 city",
        "address": "67 street",
        "capacity": 67,
        "active_sessions": 0,
        "reserved": 0,
        "tariff": Decimal("6.7"),
        "daytariff": Decimal("67.0"),
        "created_at": None,
        "latitude": Decimal("6.7"),
        "longitude": Decimal("6.7"),
        "status": "open",
        "closed_reason": None,
        "closed_date": None,
    }

def test_row_to_parking_lot():
    row = dummy_row()
    lot = parkingLot_utils.create_parking_lot_from_row(row)

    assert isinstance(lot, ParkingLot)
    assert lot.id == 676767
    assert lot.name == "67"
    assert lot.capacity == 67
    assert lot.tariff == Decimal("6.7")
    assert lot.daytariff == Decimal("67.0")


def test_row_to_parking_lot_missing_fields():
    row = dummy_row()
    row.pop("id")
    with pytest.raises(KeyError):
        parkingLot_utils.create_parking_lot_from_row(row)

    row = dummy_row()
    row.pop("name")
    with pytest.raises(KeyError):
        parkingLot_utils.create_parking_lot_from_row(row)

    row = dummy_row()
    row.pop("location")
    with pytest.raises(KeyError):
        parkingLot_utils.create_parking_lot_from_row(row)

    row = dummy_row()
    row.pop("address")
    with pytest.raises(KeyError):
        parkingLot_utils.create_parking_lot_from_row(row)

    row = dummy_row()
    row.pop("capacity")
    with pytest.raises(KeyError):
        parkingLot_utils.create_parking_lot_from_row(row)


def test_increment_active_sessions_calls_db():
    try:
        parkingLot_utils.increment_active_sessions(67, 1)
        parkingLot_utils.increment_active_sessions(67, -2)
    except Exception as e:
        pytest.fail(f"increment_active_sessions raised an exception: {e}")


def test_parking_lot_exists_returns_boolean():
    try:
        result = parkingLot_utils.parking_lot_exists(67)
        assert isinstance(result, bool)
    except Exception as e:
        pytest.fail(f"parking_lot_exists raised an exception: {e}")
