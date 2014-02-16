#!/usr/bin/env python

import os
import datetime
import sqlite3

class Task:
    def __init__(self, rowid=None, projectid=None, name=None, starttime=None, stoptime=None, active=True, synced=False, paused=False):
        self.rowid = rowid
        self.projectid = projectid
        self.name = name
        self.starttime = starttime
        self.stoptime = stoptime
        self.active = active
        self.synced = synced
        self.paused = paused

    def _pretty_elapsed_time(self):
        if not self.stoptime:
            et = datetime.datetime.now() - self.starttime
        else:
            et = self.stoptime - self.starttime

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


    def start(self, connection):
        cursor = connection.execute('insert into tasks values(?,?,?,?,?,?,?)',
                            self._tuple_values())
        connection.commit()
        self.rowid = cursor.lastrowid

        return self.rowid is not None

    def toggle_pause(self, connection):
        self.stoptime = datetime.datetime.now()
        self.active = False
        self.paused = not self.paused

        connection.execute('update tasks set stoptime=?, active=?, paused=? where rowid=?',
                            (self.stoptime, self.active, self.paused, self.rowid))

        connection.commit()


    def stop(self, connection):
        self.stoptime = datetime.datetime.now()
        self.active = False
        self.paused = False

        connection.execute('update tasks set stoptime=?, active=?, paused=? where rowid=?',
                            (self.stoptime, self.active, self.paused, self.rowid))

        connection.commit()

    def _tuple_values(self):
        return (self.projectid, 
                self.name, 
                self.starttime, 
                self.stoptime, 
                self.active, 
                self.synced, 
                self.paused)


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
        

        if project:
            # Command Line varianble takes precendence.
            self.projectname = project
        else:
            # Check the TT env variables
            tt_project = os.getenv('TT_PROJECT')
            if tt_project:
                self.projectname = tt_project
            else:
                # Are we in a virtual env?
                virtual_env = os.getenv('VIRTUAL_ENV')
                if virtual_env:
                    self.projectname = os.path.basename(os.path.basename(virtual_env))
                else:
                    # Just use the current working directory.
                    self.projectname = os.path.basename(os.getcwd())

        # Set up directories, if they do not exist
        if database_path:
            if database_path == ':memory:':
                self.database_path = database_path
            else:
                self.database_path = os.path.abspath(database_path)
                if not os.path.exists(os.path.dirname(self.database_path)):
                    os.makedirs(os.path.dirname(self.database_path))
        if not database_path:
            self.database_path = os.path.join(
                os.path.expanduser('~'), '.config', 'TimeTracker', 'tt.db')
            if not os.path.exists(os.path.dirname(self.database_path)):
                os.makedirs(os.path.dirname(self.database_path))


        self.con = sqlite3.connect(self.database_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.con.execute('create table if not exists ' \
                    'projects(name text, created datetime)')
        
        self.con.execute('create table if not exists ' \
                    'tasks(project integer, name text, starttime timestamp, ' \
                            'stoptime timestamp, active boolean, synced boolean, paused boolean)')

        result = self.con.execute('select rowid, * from projects where name=?', (self.projectname,))
        row = result.fetchone()
        if row:
            self.project_id = row[0]
        else:
            result = self.con.execute('insert into projects values(?,?)', 
                (self.projectname, datetime.datetime.now(),))
            self.project_id = result.lastrowid

        self.con.commit()

    def _get_tasks_by_taskname(self, taskname):
        result = self.con.execute('select rowid, * from tasks where name=?', (taskname,))
        results = list()
        for row in result:
            t = Task(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            results.append(t)

        return results

    def _get_active_tasks(self):
        result = self.con.execute('select rowid, project, name, starttime as "starttime [timestamp]", stoptime as "stoptime [timestamp]", active, synced, paused from tasks where active=?', (True,))

        results = list()
        for row in result:
            t = Task(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            results.append(t)

        return results

    def _get_paused_tasks(self):
        result = self.con.execute('select rowid, project, name, starttime as "starttime [timestamp]", stoptime as "stoptime [timestamp]", active, synced, paused from tasks where paused=?', (True,))

        results = list()
        for row in result:
            t = Task(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            results.append(t)

        return results

    def _sync(self, task_rowid):
        pass

    def start(self, taskname=None):
        results = self._get_active_tasks()

        if len(results) > 0:
            if taskname in [task.name for task in results]:
                print('You are already working on that task.')
            else:
                for task in results:
                    response = input('Do you want to pause %s? [Y/n]:' % (task.name))
                    if response.lower() != 'n':
                        self.toggle_pause()
                        self.start(taskname)
        else:
            if not taskname:
                taskname = 'Working on %s' % (self.projectname)

            task = Task(projectid=self.project_id,
                        name=taskname,
                        starttime=datetime.datetime.now(),
                        active=True,
                        synced=False,
                        paused=False)
            if task.start(self.con):
                print('Started %s' % (taskname))


    def pause(self, sync=False):
        results = self._get_active_tasks()

        for task in results:
            task.toggle_pause(self.con)
            print('Paused %s' % (task.name))

    def stop(self, sync=False):
        active_results = self._get_active_tasks()

        if len(active_results) > 0:
            for task in active_results:
                task.stop(self.con)

                print("%s completed in %s" % (task.name, task._pretty_elapsed_time()))

            paused_results = self._get_paused_tasks()
            for task in paused_results:
                response = input("Would you like to resume %s? [Y/n]:" % (task.name))
                if response.lower() != 'n':
                    task.start(self.con)
                    
                task.toggle_pause(self.con)
        else:
            # There are no active results, so we should stop paused tasks.
            paused_results = self._get_paused_tasks()
            for task in paused_results:
                task.stop(self.con)

        if len(active_results) == 0 and len(paused_results) == 0:
            print('There aren\'t any active or paused tasks.')

    def status(self):
        results = self._get_active_tasks()
        results = results + self._get_paused_tasks()

        if len(results) > 0:
            for task in results:
                if task.paused:
                    paused = ' [Paused]'
                else:
                    paused = ''
                
                print('%s (%s)%s' % (task.name, task._pretty_elapsed_time(), paused))
        else:
            print('There are no active tasks.')

    def close(self, sync=False):
        #This is where we would sync everything before we close
        self.con.close()