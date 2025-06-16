class RunningFilter:
    def __init__(self, tank_size=5):
        if tank_size <= 0:
            raise ValueError("tank_size must be a positive integer")
        self.tank_size = tank_size
        self.tank = []

    def add(self, raw_value):
        if raw_value is None:
            return None
        self.tank.append(raw_value)
        if len(self.tank) > self.tank_size:
            self.tank.pop(0)
        return self.average()

    def average(self):
        """Return average of the current tank values"""
        if not self.tank:
            return None
        return round(sum(self.tank) / len(self.tank), 2)
