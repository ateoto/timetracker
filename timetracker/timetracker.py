#!/usr/bin/env python

import os
import datetime
import sqlite3

class Task:
    def __init__(self, rowid, projectid, name, start, stop, active, synced, paused):
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
        self.paused = paused

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

        try:
            self.allow_sync = bool(int(os.getenv('TT_ALLOW_SYNC', default=False)))
        except ValueError:
            print('WARNING:')
            print('Please set TT_ALLOW_SYNC to 1 to allow syncing, or 0 to disallow syncing with the server.')
            print('Syncing has been disabled for this run.')
            self.allow_sync = False
            
        self.server = os.getenv('TT_SERVER_ADDRESS')
        self.api_token = os.getenv('TT_ACCESS_TOKEN')

        # Set up directories, if they do not exist
        if database_path:
            self.database_path = os.path.abspath(database_path)
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
                            'stop datetime, active boolean, synced boolean, paused boolean)')
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

    def _get_tasks_by_taskname(self, taskname):
        con = sqlite3.connect(self.database_path)
        result = con.execute('select rowid, * from tasks where name=?', (taskname,))
        results = list()
        for row in result:
            t = Task(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            results.append(t)

        con.close()

        return results

    def _get_active_tasks(self):
        con = sqlite3.connect(self.database_path)
        result = con.execute('select rowid, * from tasks where active=?', (True,))

        results = list()
        for row in result:
            t = Task(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            results.append(t)

        con.close()

        return results

    def _get_paused_tasks(self):
        con = sqlite3.connect(self.database_path)
        result = con.execute('select rowid, * from tasks where paused=?', (True,))

        results = list()
        for row in result:
            t = Task(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            results.append(t)

        con.close()

        return results

    def _sync(self, task_rowid):
        pass

    def start(self, taskname=None, sync=False):
        results = self._get_active_tasks()

        if len(results) > 0:
            if taskname in [task.name for task in results]:
                print('You are already working on that task.')
            else:
                for task in results:
                    response = input('Do you want to pause %s? [Y/n]:' % (task.name))
                    if response.lower() != 'n':
                        self.pause()
                        self.start(taskname)
        else:
            if not taskname:
                taskname = 'Working on %s' % (self.projectname)
            con = sqlite3.connect(self.database_path)
            cursor = con.execute('insert into tasks ' \
                        '(project, name, start, active, synced, paused) ' \
                        'values(?,?,?,?,?,?)', (
                        self.project_id, 
                        taskname, 
                        datetime.datetime.now(),
                        True,
                        False,
                        False))

            print('Started %s' % (taskname))

            con.commit()
            con.close()

            if self.allow_sync or sync:
                self._sync(cursor.lastrowid)


    def pause(self, sync=False):
        results = self._get_active_tasks()

        con = sqlite3.connect(self.database_path)
        for task in results:
            con.execute('update tasks set stop=?, active=?, paused=? where rowid=?',
                        (datetime.datetime.now(), False, True, task.rowid,))
            print('Paused %s' % (task.name))
        con.commit()
        con.close()

    def stop(self, sync=False):
        active_results = self._get_active_tasks()
        paused_results = self._get_paused_tasks()

        con = sqlite3.connect(self.database_path)
        if len(active_results) > 0:
            con = sqlite3.connect(self.database_path)
            for task in active_results:
                task.stop = datetime.datetime.now()
                task.active = False
                con.execute('update tasks set stop=?, active=? where rowid=?', 
                            (task.stop, task.active, task.rowid,))

                print("%s completed in %s" % (task.name, task._pretty_elapsed_time()))

        con.commit()

        if len(paused_results) > 0:
            for task in paused_results:
                response = input("Would you like to resume %s? [Y/n]:" % (task.name))
                if response.lower() != 'n':
                    self.start(task.name)
                
                con.execute('update tasks set paused=? where rowid=?',
                            (False, task.rowid,))
        con.commit()
        con.close()

        if len(active_results) == 0 and len(paused_results) == 0:
            print('There aren\'t any active or paused tasks.')

    def status(self):
        results = self._get_active_tasks()
        results = results + self._get_paused_tasks()

        if len(results) > 0:
            for task in results:
                if not task.paused:
                    print('%s (%s)' % (task.name, task._pretty_elapsed_time()))
                else:
                    print('%s (%s) [Paused]' % (task.name, task._pretty_elapsed_time()))
        else:
            print('There are no active tasks.')