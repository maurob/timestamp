"""
Command line application to timestamp events
"""
__author__ = 'Mauro Bruni'
__email___ = 'maumarbru@gmail.com'

from datetime import datetime, timedelta
import sys
import os
from collections import namedtuple

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
log_file_name = os.path.join(BASE_DIR, 'list.txt')

text_editor = 'subl'

LAST_REPORT = 'LAST_REPORT'

main_end   = 'end'
main_start = 'start'

events = [
    main_end,
    main_start,
    LAST_REPORT,
    ]


def show_events():
    print
    for i, event in enumerate(events):
        print '\t{0}: {1}'.format(i, event)

Period = namedtuple('Period', 'start end')

class Metric(object):
    def __init__(self):
        self.periods = []

    def analize(self, start, end):
        """Analize a new time interval *start* - *end*"""
        self.periods.append(Period(start, end))

    @property
    def value(self):
        """Return the calculated value"""

class WeeklyMeanMetric(Metric):
    @property
    def value(self):
        sum_periods = sum((p.end - p.start for p in self.periods), timedelta(0))
        try:
            return sum_periods.total_seconds() / 3600.0 / self.weeks
        except ZeroDivisionError:
            return 0

    @property
    def weeks(self):
        periods = sorted(self.periods)
        try:
            initial = periods[0].start
            final = periods[-1].end
        except IndexError:
            return 0
        return (final - initial).total_seconds() / timedelta(days=7).total_seconds()



def show_stats():
    t0 = None
    a_week = timedelta(days=7)
    a_day = timedelta(days=1)
    now = datetime.now()
    last_report_time = now
    last_report_accum = timedelta(0)
    total = timedelta(0)
    last_week = timedelta(0)
    last_day = timedelta(0)
    weekly_mean = WeeklyMeanMetric()
    for event, timestamp in load():
        if event == main_start:
            t0 = timestamp
        elif event == main_end:
            if t0 is None:
                raise ValueError('{} missing before {}'.format(main_start, main_end))
            t = timestamp - t0
            total += t
            weekly_mean.analize(t0, timestamp)
            if (now - t0) < a_week:
                last_week += t
            if (now - t0) < a_day:
                last_day += t
            if t0 > last_report_time:
                last_report_accum += t
            t0 = None
        elif event == LAST_REPORT:
            last_report_time = timestamp
            last_report_accum = timedelta(0)

    print('Last day:  {}'.format(last_day))
    print('Last week: {}'.format(last_week))
    if weekly_mean.weeks >= 1:
        print('Weekly mean: {} hour/week along {} weeks'.format(weekly_mean.value, weekly_mean.weeks))
    print('Total:     {}'.format(total))
    print('Since last report: {}'.format(last_report_accum))

def select(event_id=None):
    show_stats()
    try:
        if event_id is None:
            show_events()
            id_str = raw_input('Choose an event: ')
            if len(id_str) > 0:
                return int(id_str)
            else:
                print "Doing nothing :P"
                exit(0)
        else:
            if event_id >= len(events):
                show_events()
                print "Error: Event {0} not found".format(event_id)
                exit(1)
            else:
                return event_id
    except KeyboardInterrupt:
        print
        exit(0)

def clear_comment(text_line):
    try:
        i = text_line.index('#')
        return text_line[:i]
    except ValueError:
        return text_line

def load():
    """ Load `log_file_name` and return an object oriented list """
    L = []
    try:
        for line in open(log_file_name):
            line = clear_comment(line)
            if len(line.strip()) > 0:
                event, str_time = split(line)
                time = datetime.strptime(str_time.strip(), "%Y-%m-%d %H:%M:%S.%f")
                L.append((event.strip(), time))
    finally:
        return L

def split(line):
    """ Split between event name and time """
    i1 = line.find(' ')
    i2 = line.find('\t')
    if i1 == -1: i1 = len(line)
    if i2 == -1: i2 = len(line)
    if i1 < i2:
        i = i1
    elif i2 < i1:
        i = i2
    else:
        raise ValueError("split doesn't find a ' ' or '\\t' in '%s'" % line.strip())
    return line[:i].strip(), line[i:].strip()

def verify_insertion(event):
    """ Return True if `event` is `main_end` for a last registered `main_start` and viceversa """
    L = load()
    starts = [item[1] for item in L if item[0] == main_start]
    if len(starts) == 0 and event == main_end:
        print "You must define at least one '{}' event first".format(main_start)
        return False
    ends = [item[1] for item in L if item[0] == main_end]
    if len(ends) == 0 or starts[-1] > ends[-1]:
        if event == main_end:
            return True
        else:
            if len(starts) == 0:
                return True
            print "You'er trying to insert '{0}' when the last registered was at {1}.".format(event, starts[-1])
            return False
    elif len(starts) == 0 or starts[-1] < ends[-1]:
        if event == main_start:
            return True
        elif event == main_end:
            print "You're trying to insert '{0}' when the last registered was at {1}.".format(event, ends[-1])
            return False
        else:
            return True
    else:
        print "There's no time between {0} and {1}".format(starts[-1], ends[-1])
        return False

def stamp(event_id):
    while True:
        if verify_insertion(events[event_id]):
            record = '{0}\t{1}'.format(events[event_id], str(datetime.now()))
            with open(log_file_name, 'a+') as f:
                f.write(record+'\n')
            print record
            break
        else:
            print "Timestamp not inserted."
            answer = raw_input("Do you want to insert the remaining timestamp manually (y/[n])? ")
            if len(answer) > 0 and answer.lower() == 'y':
                os.system(text_editor+' '+log_file_name)
                print "re-trying timestamp ..."
            else:
                print "Bye bye :/"
                break

def mean_hours_per_day():
    """ Return the mean hours per day using the registered days """
    L = load()
    accum, days = timedelta(0), 0
    for event, time in L:
        if event == main_start:
            t = time
        elif event == main_end:
            d = time - t
            if d > timedelta(days=1):
                print "Warning: '{0}' is too long for the working day since '{1}' to '{2}'".format(d, t, time)
            else:
                accum, days = accum + d, days + 1
    return (accum/days).seconds/3600.0
#    return accum.seconds/days

def days_hours(time):
    t = time.time()
    d = time.date()
    days = (d.day-1) + (d.month-1)*30.5 + d.year*365.25
    hours = t.hour + t.minute/60.0
    if hours < 5.0:
        hours += 24.0
        days -= 1
    return days, hours

def plot():
    import pylab as pl
    for event, time in load():
        color = {main_start:'g*', main_end:'r*'}
        days, hours = days_hours(time)
        try:
            pl.plot([days], [hours], color[event])
        except KeyError:
            pass
    pl.grid(True)
    pl.xlabel('Time [day]')
    pl.ylabel('Day interval [hours]')
    pl.show()

def plot2():
    import pylab as pl
    hs, ds = [], []
    for event, time in load():
        if event == main_start:
            start_time = time
        elif event == main_end:
            d0, h0 = days_hours(start_time)
            d1, h1 = days_hours(time)
            hs.append((h0, h1))
            ds.append((d0, d1))
            pl.plot([d0, d1], [h0, h1], 'b')
    ihs, fhs = zip(*hs)
    ids, fds = zip(*ds)
    pl.plot(ids, ihs, 'g')
    pl.plot([ids[0], ids[-1]], [pl.mean(ihs)]*2, 'g--')
    pl.plot(fds, fhs, 'r')
    pl.plot([fds[0], fds[-1]], [pl.mean(fhs)]*2, 'r--')
    f, i = pl.mean(fhs), pl.mean(ihs)
    pl.plot([fds[0], fds[-1]], [(f+i)/2]*2, 'b--')
    print i, f, f-i, (f+i)/2
    std_i, std_f = pl.std(ihs), pl.std(fhs)
    print std_i, std_f
    pl.xlim(ids[0], fds[-1])
    pl.ylim(4, 28)
    pl.grid(True)
    pl.xlabel('Time [day]')
    pl.ylabel('Day interval [hours]')
    pl.show()

if __name__ == '__main__':
    try:
        event_id = select(int(sys.argv[1]))
    except IndexError:
        event_id = select()

    stamp(event_id)
    show_stats()
