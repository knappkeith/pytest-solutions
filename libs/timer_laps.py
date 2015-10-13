import stopwatch
from collections import namedtuple

class LapWatch(stopwatch.Timer):
    lap_tuple = namedtuple('lap', ['total_time', 'lap_time', 'lap_name'])

    def __init__(self):
        self.laps = lap_list()
        super(LapWatch, self).__init__()

    def lap(self, lap_name=None):
        total = self.elapsed
        if not lap_name:
            lap_name = "Lap %d" % (len(self.laps) + 1)
        if len(self.laps) == 0:
            lap_time = total
        else:
            lap_time = total - self.laps[-1][0]
        self.laps.append(self.lap_tuple(total, lap_time, lap_name))
        return lap_time

    def reset_laps(self):
        self.laps = lap_list()

class lap_list(list):
    def __str__(self):
        printer = []
        for i in self:
            if i.lap_time > 60:
                printer.append(":  ".join([i.lap_name, secs_to_str(i.lap_time)]))
            else:
                printer.append(":  ".join([i.lap_name, str(round(i.lap_time,3)) + "s"]))
        return "\n".join(printer)

def secs_to_str(seconds):
    hrs = int(seconds/3600)
    time_left = seconds - (hrs * 3600)
    mins = int(time_left/60)
    time_left -= (mins * 60)
    secs = round(time_left, 3)
    if hrs > 0:
        rtn_str = str(hrs) + "h " + str(mins) + "m " + str(secs) + "s"
    elif mins > 0:
        rtn_str = str(mins) + "m " + str(secs) + "s"
    else:
        rtn_str = str(secs) + "s"
    return rtn_str

