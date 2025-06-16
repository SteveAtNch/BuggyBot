import ntptime
import time

class TimeManager:
    def __init__(self, tz_offset_std=-5, tz_offset_dst=-4, dst_enabled=True):
        self.tz_offset_std = tz_offset_std
        self.tz_offset_dst = tz_offset_dst
        self.dst_enabled = dst_enabled

    def sync_time(self):
        try:
            ntptime.settime()
        except Exception:
            pass

    def find_nth_weekday(self, year, month, weekday, n):
        count = 0
        for day in range(1, 32):
            try:
                if time.localtime(time.mktime((year, month, day, 0, 0, 0, 0, 0)))[6] == weekday:
                    count += 1
                    if count == n:
                        return day
            except:
                break
        return None

    def is_dst(self, tm):
        if not self.dst_enabled:
            return False
        year, month, mday, hour = tm[0], tm[1], tm[2], tm[3]
        dst_start = self.find_nth_weekday(year, 3, 6, 2)  # 2nd Sunday in March
        dst_end = self.find_nth_weekday(year, 11, 6, 1)   # 1st Sunday in November

        if month < 3 or (month == 3 and (mday < dst_start or (mday == dst_start and hour < 2))):
            return False
        if month > 11 or (month == 11 and (mday > dst_end or (mday == dst_end and hour >= 2))):
            return False
        return True

    def get_local_time(self):
        utc = time.localtime()
        ts_utc = time.mktime(utc)
        if self.is_dst(utc):
            offset = self.tz_offset_dst * 3600
            tzname = "EDT"
        else:
            offset = self.tz_offset_std * 3600
            tzname = "EST"
        local_ts = ts_utc + offset
        local = time.localtime(local_ts)
        return local, tzname
