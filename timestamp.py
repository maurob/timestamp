"""
Command line application to timestamp events
"""
__author__ = 'Mauro Bruni'
__email___ = 'mauamrbru@gmail.com'

from datetime import datetime
import sys
import os

log_file_name = '~/.timestamp_py'

events = [
    'endday',
    'startday',
    'almuerzo',
    'eagle',
    'eagle-simtool',
    'misc',
    'it',
    'stop',
    ]


def show_events():
    print
    for i, event in enumerate(events):
        print '\t{0}: {1}'.format(i, event)


def select(event_id=None):
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


def stamp(event_id):
    record = '{0}\t{1}'.format(events[event_id], str(datetime.now()))
    with open(os.path.expanduser(log_file_name), 'a+') as f:
        f.write(record+'\n')
    print record
       

if __name__ == '__main__':
    try:
        event_id = select(int(sys.argv[1]))
    except IndexError:
        event_id = select()

    stamp(event_id)
