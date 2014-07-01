"""
Command line application to timestamp events
"""
__author__ = 'Mauro Bruni'
__email___ = 'mauamrbru@gmail.com'

from datetime import datetime
import sys
import os

log_file_name = os.path.expanduser('~/.timestamp_py')

text_editor = 'emacs'

main_end   = 'endday'
main_start = 'startday'

events = [
    main_end,
    main_start,
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

def load():
    """ Load `log_file_name` and return an object oriented list """
    L = []
    for line in open(log_file_name):
        if len(line.strip()) > 0:
            event, str_time = line.split('\t')
            time = datetime.strptime(str_time.strip(), "%Y-%m-%d %H:%M:%S.%f")
            L.append((event.strip(), time))
    return L

def verify_insertion(event):
    """ Return True if `event` is `main_end` for a last registered `main_start` and viceversa """
    L = load()
    starts = [item[1] for item in L if item[0] == main_start]
    ends = [item[1] for item in L if item[0] == main_end]
    if len(ends) == 0 or starts[-1] > ends[-1]:
        if event == main_end:
            return True
        else:
            print "You'er trying to insert '{0}' when the last registered was at {1}.".format(event, starts[-1])
            return False
    elif len(starts) == 0 or starts[-1] < ends[-1]:
        if event == main_start:
            return True
        else:
            print "You'er trying to insert '{0}' when the last registered was at {1}.".format(event, ends[-1])
            return False
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

       

if __name__ == '__main__':
    try:
        event_id = select(int(sys.argv[1]))
    except IndexError:
        event_id = select()

    stamp(event_id)
