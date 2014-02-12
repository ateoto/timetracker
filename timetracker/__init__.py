import argparse

from .tt import TimeTracker

def process_commands():
    parser = argparse.ArgumentParser(description='Keep track of tasks and time.')
    parser.add_argument('action', help='Start/stop tracking, sync database to server.')
    parser.add_argument('taskname', nargs='?')

    parser.add_argument('--database', 
                        help='Specify a path for the database.')

    parser.add_argument('--project',
                        help='Specify a projectname to work on.'\
                        'If not set, defaults to current directory.')

    args = parser.parse_args()

    tt = TimeTracker(args.database, args.project)

    if args.action == 'start':
        tt.start(args.taskname)
    if args.action == 'stop':
        tt.stop(args.taskname)
    if args.action == 'list':
        tt.list(args.taskname)