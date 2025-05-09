def to_rub(cents: int) -> str:
    rubles = cents // 100
    cents = cents % 100
    return f'{rubles}.{str(cents).zfill(2)}'
