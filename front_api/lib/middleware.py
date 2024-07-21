from datetime import datetime
import time
from sqlalchemy import text

from lib.mysql import get_engine
from shared.lib.utils import *

def log_api_perf(endpoint: str, start_time: float, status_code: int):
    # Calculer la durée en millisecondes
    duration_ms = (time.perf_counter() - start_time) * 1000
    # Obtenir l'horodatage actuel avec des millisecondes
    call_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    # print(f"Timestamp: {timestamp}, Route: {route}, Duration: {duration} ms, Status Code: {status_code}")

    engine = get_engine()
    with engine.connect() as connection:
        statement = text('INSERT INTO karma.api_log_perf(call_datetime, endpoint, duration_ms, status_code) VALUES (:call_datetime, :endpoint, :duration_ms, :status_code);')
        try:
            connection.execute(statement,{"call_datetime": call_datetime, "endpoint": endpoint,"duration_ms": duration_ms,"status_code":status_code})
            # Default rollback behavior with alchemy, so commit change !!!!
            connection.commit()
        except ValueError:
            connection.rollback()
            add_log('/shared/log.txt', ValueError.__str__)
