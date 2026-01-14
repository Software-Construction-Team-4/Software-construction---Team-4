import pytest
from datetime import datetime, timedelta
from LogicLayer import sessionLogic as ps_logic
from DataModels.parkingSessionModel import ParkingSession

def dummy_session_row():
    return {
        "id": 676767,
        "parking_lot_id": 67,
        "session": 1,
        "user": 67,
        "licenseplate": "67-AAA-7",
        "started": datetime.now() - timedelta(minutes=30),
        "stopped": None,
        "duration_minutes": 0,
        "cost": 0,
        "payment_status": "pending"
    }

def test_start_parking_session():
    try:
        result = ps_logic.start_parking_session(
            parking_lot_id=67,
            licenseplate="67-AAA-7",
            user_id=67
        )
        assert isinstance(result, dict)
    except Exception as e:
        pytest.fail(f"start_parking_session raised an exception: {e}")

def test_stop_parking_session():
    try:
        result = ps_logic.stop_parking_session(user_id=67)
        assert result is None or isinstance(result, ParkingSession)
    except Exception as e:
        pytest.fail(f"stop_parking_session raised an exception: {e}")

def test_mark_user_sessions_paid_basic_call():
    try:
        ps_logic.mark_user_sessions_paid(user_id=67)
    except Exception as e:
        pytest.fail(f"mark_user_sessions_paid raised an exception: {e}")

def test_get_unpaid_session_basic_call():
    try:
        session = ps_logic.get_unpaid_session(user_id=67)
        assert session is None or isinstance(session, ParkingSession)
    except Exception as e:
        pytest.fail(f"get_unpaid_session raised an exception: {e}")

def test_refund_session_basic_call():
    try:
        ps_logic.refund_session(session_id=676767)
    except Exception as e:
        pytest.fail(f"refund_session raised an exception: {e}")
