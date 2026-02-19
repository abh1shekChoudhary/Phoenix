from datetime import datetime, timedelta

COOLDOWN_MINUTES = 5

def is_in_cooldown(incident):
    if not incident.cooldown_until:
        return False
    return datetime.utcnow() < incident.cooldown_until
