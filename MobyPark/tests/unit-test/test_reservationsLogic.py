from datetime import datetime, timedelta
from LogicLayer import reservationsLogic as res_logic
from DataModels.reservationsModel import Reservations

def dummy_reservation():
    now = datetime.now()
    return Reservations(
        id=12345,
        user_id=67,
        parking_lot_id=10,
        vehicle_id=5,
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=2),
        status="pending",
        created_at=now,
        cost=20,
        updated_at=None
    )

def test_create_reservation():
    original_save = res_logic.save_reservation
    try:
        res_logic.save_reservation = lambda res: 12345
        res_id = res_logic.create_reservation(dummy_reservation())
        assert res_id == 12345
    finally:
        res_logic.save_reservation = original_save

def test_get_reservation():
    original_get = res_logic.get_reservation_by_id
    try:
        fake_row = {
            "id": 12345,
            "user_id": 67,
            "parking_lot_id": 10,
            "vehicle_id": 5,
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "status": "pending",
            "created_at": datetime.now(),
            "cost": 20,
            "updated_at": None
        }
        res_logic.get_reservation_by_id = lambda rid: fake_row
        res = res_logic.get_reservation(12345)
        assert res.id == 12345
        assert res.status == "pending"
    finally:
        res_logic.get_reservation_by_id = original_get

def test_update_reservation_logic():
    original_update = res_logic.update_reservation
    try:
        calls = []
        res_logic.update_reservation = lambda res: calls.append(res)
        res = dummy_reservation()
        res_logic.update_reservation_logic(res)
        assert calls[0] == res
    finally:
        res_logic.update_reservation = original_update

def test_delete_reservation_logic():
    original_delete = res_logic.delete_reservation
    try:
        calls = []
        res_logic.delete_reservation = lambda rid: calls.append(rid)
        res_logic.delete_reservation_logic(12345)
        assert calls[0] == 12345
    finally:
        res_logic.delete_reservation = original_delete

def test_get_reservation_by_user_id():
    original_load = res_logic.load_all_reservations
    try:
        res_logic.load_all_reservations = lambda: [
            {
                "id": 1,
                "user_id": 67,
                "parking_lot_id": 10,
                "vehicle_id": 5,
                "start_time": datetime.now(),
                "end_time": datetime.now(),
                "status": "pending",
                "created_at": datetime.now(),
                "cost": 10,
                "updated_at": None
            }
        ]
        res = res_logic.get_reservation_by_user_id(67)
        assert res is not None
        assert res.user_id == 67
        assert res.status == "pending"
    finally:
        res_logic.load_all_reservations = original_load

def test_get_all_reservations():
    original_load = res_logic.load_all_reservations
    try:
        res_logic.load_all_reservations = lambda: [
            {
                "id": 1,
                "user_id": 67,
                "parking_lot_id": 10,
                "vehicle_id": 5,
                "start_time": datetime.now(),
                "end_time": datetime.now(),
                "status": "pending",
                "created_at": datetime.now(),
                "cost": 10,
                "updated_at": None
            }
        ]
        reservations = res_logic.get_all_reservations()
        assert isinstance(reservations, list)
        for r in reservations:
            assert isinstance(r, Reservations)
    finally:
        res_logic.load_all_reservations = original_load

def test_get_reservations_count_today():
    original_count = res_logic.get_today_reservations_count_by_lot
    try:
        res_logic.get_today_reservations_count_by_lot = lambda: 5
        count = res_logic.get_reservations_count_today()
        assert count == 5
    finally:
        res_logic.get_today_reservations_count_by_lot = original_count

def test_process_missed_sessions():
    original_create = res_logic.create_missed_parking_sessions_for_date
    try:
        calls = []
        res_logic.create_missed_parking_sessions_for_date = lambda date: calls.append(date)
        target_date = datetime.now().date()
        res_logic.process_missed_sessions(target_date)
        assert calls[0] == target_date
    finally:
        res_logic.create_missed_parking_sessions_for_date = original_create
