import argparse

from .timetracker import TimeTracker

def process_commands():
    parser = argparse.ArgumentParser(description='Keep track of tasks and time.')
    parser.add_argument('action', help='Start/stop tracking, sync database to server.')
    parser.add_argument('taskname', nargs='?', help='Define a taskname to keep track of')

    parser.add_argument('--database', 
                        help='Specify a path for the database.')

    parser.add_argument('--sync',
                        help='TimeTracker will attempt to sync with the server. ' \
                        'To avoid adding this everytime, you can set the environment '\
                        'variable TT_ALLOW_SYNC to 1',
                        action='store_true')

    parser.add_argument('--project',
                        help='Specify a projectname to work on.'\
                        'If not set, defaults to name of current directory.')

    args = parser.parse_args()

    tt = TimeTracker(args.database, args.project)

    if args.action == 'start':
        tt.start(taskname=args.taskname, sync=args.sync)
    if args.action == 'stop':
        tt.stop(args.sync)
    if args.action == 'pause':
        tt.pause(args.sync)
    if args.action == 'status':
        tt.status()