import time
import os

class MicroLogger:
    def __init__(self, log_dir="/sd/logs", log_name="log.txt"):
        self.log_dir = log_dir
        self.filepath = f"{self.log_dir}/{log_name}"
        self._init_log()

    def _init_log(self):
        try:
            import os
            # Attempt to create the directory if it doesn't exist
            try:
                os.mkdir(self.log_dir)
            except OSError as e:
                if e.args[0] != 17:  # 17 = EEXIST
                    raise  # Re-raise if it's a different error
            self._write_line("00000000 00:00:00.000,,INFO,--- BOOT ---")

        except Exception as e:
                print("Logger init failed:", e)


    def _dir_exists(self, path):
        try:
            return path in os.listdir("/".join(path.split("/")[:-1]) or "/")
        except:
            return False

    def _get_timestamp(self):
        t = time.localtime()
        ms = time.ticks_ms() % 1000
        return "{:04d}{:02d}{:02d} {:02d}:{:02d}:{:02d}.{:03d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5], ms
        )

    def _write_line(self, line):
        try:
            with open(self.filepath, "a") as f:
                f.write(line + "\n")
        except Exception as e:
            print("Logging write failed:", e)

    def info(self, tz, message):
        timestamp = self._get_timestamp()
        self._write_line(f"{timestamp},{tz},INFO,{message}")

    def error(self, tz, message):
        timestamp = self._get_timestamp()
        self._write_line(f"{timestamp},{tz},ERROR,{message}")
