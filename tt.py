#!/usr/bin/env python

import argparse
import os
import datetime
import sqlite3


parser = argparse.ArgumentParser(description='Keep track of tasks and time.')
parser.add_argument('action', help='Start/stop tracking, sync database to server.')
parser.add_argument('taskname', nargs='?')

parser.add_argument('--database', 
                    help='Specify a path for the database.')

parser.add_argument('--project',
                    help='Specify a projectname to work on.'\
                    'If not set, defaults to current directory.')

class Task:
    def __init__(self, rowid, projectid, name, start, stop, active, synced):
        self.rowid = rowid
        self.projectid = projectid
        self.name = name
        if start:
            self.start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S.%f')
        else:
            self.start = None
        if stop:
            self.stop = datetime.datetime.strptime(stop, '%Y-%m-%d %H:%M:%S.%f')
        else:
            self.stop = None
        self.active = active
        self.synced = synced

    def _pretty_elapsed_time(self):
        if not self.stop:
            et = datetime.datetime.now() - self.start
        else:
            et = self.stop - self.start

        # Pretty Elapsed time: adapted from django.utils.timesince
        chunks = (
            (60 * 60, 'hours'),
            (60, 'minutes')
        )

        since = et.days * 24 * 60 * 60 + et.seconds
        for i, (seconds, name) in enumerate(chunks):
            count = since // seconds
            if count != 0:
                break
        pretty = "%i %s" % (count, name)

        if i + 1 < len(chunks):
            # Now get the second item
            seconds2, name2 = chunks[i + 1]
            count2 = (since - (seconds * count)) // seconds2
            if count2 != 0:
                pretty = "%s, %i %s" % (pretty, count2, name2)     
                
        return pretty 

    def __str__(self):
        return "[%s] Elapsed Time: %s" % (self.name, self._pretty_elapsed_time())

    def __repr__(self):
        return self.__str__()

class TimeTracker:
    def __init__(self, database_path=None, project=None):
        # Set up directories, if they do not exist
        if database_path:
            self.database_path = database_path
            if not os.path.exists(os.path.dirname(self.database_path)):
                os.makedirs(os.path.dirname(self.database_path))
        if not database_path:
            self.database_path = os.path.join(
                os.path.expanduser('~'), '.config', 'TimeTracker', 'tt.db')
            if not os.path.exists(os.path.dirname(self.database_path)):
                os.makedirs(os.path.dirname(self.database_path))

        # Create projects and tasks tables if they do not exist
        if project:
            self.projectname = project
        else:
            self.projectname = os.path.basename(os.getcwd())

        con = sqlite3.connect(self.database_path)
        con.execute('create table if not exists ' \
                    'projects(name text, created datetime)')
        con.execute('create table if not exists ' \
                    'tasks(project integer, name text, start datetime, ' \
                            'stop datetime, active boolean, synced boolean)')
        result = con.execute('select rowid, * from projects where name=?', (self.projectname,))
        row = result.fetchone()
        if row:
            self.project_id = row[0]
        else:
            result = con.execute('insert into projects values(?,?)', 
                (self.projectname, datetime.datetime.now(),))
            result = con.execute('select rowid, * from projects where name=?', 
                (self.projectname,))
            row = result.fetchone()
            self.project_id = row[0]

        con.commit()
        con.close()

    def _get_active_tasks_by_name(self, taskname=None, everything=False):
        con = sqlite3.connect(self.database_path)
        if not everything:
            if taskname:
                result = con.execute('select rowid, * from tasks where project=? ' \
                                    'and name=? and active=?', 
                                    (self.project_id, taskname, True,))
            else:
                result = con.execute('select rowid, * from tasks where project=? ' \
                                    'and name is null and active=?', 
                                    (self.project_id, True,))
        else:
            result = con.execute('select rowid, * from tasks where project=? '\
                                    'and active=?',
                                    (self.project_id, True,))


        results = list()
        for row in result:
            t = Task(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            results.append(t)

        con.close()

        return results

    def start(self, taskname=None):
        results = self._get_active_tasks_by_name(taskname)

        if len(results) > 0:
            # For right now, lets just tell the user that they can't do this.
            # In the future, lets make this more interactive.
            print('There are %i active tasks with the same name, ' \
                    'you should complete them before starting another.' 
                    % len(results))
        else:
            con = sqlite3.connect(self.database_path)
            con.execute('insert into tasks ' \
                        '(project, name, start, active, synced) ' \
                        'values(?,?,?,?,?)', (
                        self.project_id, 
                        taskname, 
                        datetime.datetime.now(),
                        True,
                        False))

            con.commit()
            con.close()

    def stop(self, taskname=None):
        results = self._get_active_tasks_by_name(taskname)

        if len(results) > 0:
            con = sqlite3.connect(self.database_path)
            for task in results:
                task.stop = datetime.datetime.now()
                task.active = False
                con.execute('update tasks set stop=?, active=? where rowid=?', 
                            (task.stop, task.active, task.rowid,))

                print("%s completed. Elapsed Time: %s" % (task.name, task._pretty_elapsed_time()))
            con.commit()
            con.close()
        else:
            print('There does not appear to be any open tasks with that name.')

    def list(self, taskname=None):
        if not taskname:
            #We should take this to mean ALL tasks
            results = self._get_active_tasks_by_name(everything=True)
        else:
            results = self._get_active_tasks_by_name(taskname)

        if len(results) > 0:
            print('Open Tasks:')
            print('===========')
            for task in results:
                print(task)

if __name__ == '__main__':
    args = parser.parse_args()

    tt = TimeTracker(args.database, args.project)

    if args.action == 'start':
        tt.start(args.taskname)
    if args.action == 'stop':
        tt.stop(args.taskname)
    if args.action == 'list':
        tt.list(args.taskname)