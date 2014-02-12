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

    def start(self, taskname=None):
        results = self._get_active_tasks()

        if len(results) > 0:
            response = input('Do you want to pause %s? [Y/n]:' % (results[0].name))
            if response.lower() is not 'n':
                self.pause(results[0].name)
                self.start(taskname)
        else:
            if not taskname:
                taskname = 'Working on %s' % (self.projectname)
            con = sqlite3.connect(self.database_path)
            con.execute('insert into tasks ' \
                        '(project, name, start, active, synced, paused) ' \
                        'values(?,?,?,?,?,?)', (
                        self.project_id, 
                        taskname, 
                        datetime.datetime.now(),
                        True,
                        False,
                        False))

            con.commit()
            con.close()

    def pause(self):
        con = sqlite3.connect(self.database_path)
        
        results = con.execute('select rowid, name from tasks where active=?', (True,))
        for task in results:
            rowid = task[0]
            con.execute('update tasks set stop=?, active=?, paused=? where rowid=?',
                        (datetime.datetime.now(), False, True, rowid,))
            print('Paused %s' % (task[1]))
        con.commit()
        con.close()


    def stop(self):
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
                if response.lower() is not 'n':
                    self.start(task.name)
                else: 
                    con.execute('update tasks set paused=? where rowid=?',
                                (False, task.rowid,))
        con.commit()
        con.close()

        if len(active_results) == 0 and len(paused_results) == 0:
            print('There aren\'t any active or paused tasks.')

    def status(self):
        results = self._get_active_tasks()

        if len(results) > 0:
            for task in results:
                print('%s Elapsed Time: %s' % (task.name, task._pretty_elapsed_time()))