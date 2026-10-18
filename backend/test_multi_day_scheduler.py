
from app.optimization.multi_day_scheduler import (
    schedule_multi_day_trip,
)

result = schedule_multi_day_trip(
    distance_km=1200,
    daily_working_hours=10,
)

print(result)
