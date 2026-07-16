def get_world_state(tick):
    # 360-day year
    day_of_year = tick % 360
    
    # Sun Eclipse (last 7 days of year)
    if day_of_year >= 354:
        return {"status": "ECLIPSE_MODE"}
    
    # Moon Wobble (4 Quadrants)
    quadrant = (tick // 90) % 4 
    return {"quadrant": quadrant, "status": "ACTIVE"}
