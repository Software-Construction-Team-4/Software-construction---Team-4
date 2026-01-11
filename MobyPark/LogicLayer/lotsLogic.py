from DataAccesLayer.db_utils_parkingLots import (
    load_all_parking_lots_from_db,
    load_parking_lot_row_by_id,
    update_parking_lot,
    create_parking_lot_from_row,
    load_active_session_count
)
from DataAccesLayer.db_utils_reservations import (
    create_missed_parking_sessions,
    get_today_reservations_count_by_lot
)

def load_parking_lots():
    create_missed_parking_sessions()
    rows = load_all_parking_lots_from_db()
    today_reservations = get_today_reservations_count_by_lot()

    parking_lots = {}

    for row in rows:
        lot_id = str(row["id"])
        reserved_amount = today_reservations.get(lot_id, 0)
        active_amount = load_active_session_count(lot_id)

        update_parking_lot(
            lot_id,
            {
                "reserved": reserved_amount,
                "active_sessions": active_amount
            }
        )

        row["reserved"] = reserved_amount
        row["active_sessions"] = active_amount
        parking_lots[lot_id] = create_parking_lot_from_row(row)

    return parking_lots

def load_parking_lot_by_id(lot_id):
    create_missed_parking_sessions()
    row = load_parking_lot_row_by_id(lot_id)
    if not row:
        return None

    today_reservations = get_today_reservations_count_by_lot()
    reserved_amount = today_reservations.get(str(lot_id), 0)
    active_amount = load_active_session_count(lot_id)

    update_parking_lot(
        lot_id,
        {
            "reserved": reserved_amount,
            "active_sessions": active_amount
        }
    )

    row["reserved"] = reserved_amount
    row["active_sessions"] = active_amount
    return create_parking_lot_from_row(row)
