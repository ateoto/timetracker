import argparse
import json
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
	def __init__(self, projectid, taskname, start, stop, active, synced):
		self.projectid = projectid
		self.taskname = taskname
		self.start = start
		self.stop = stop
		self.active = active
		self.synced = synced

	def __str__(self):
		return "%s active: %s" % (self.taskname, self.active)

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
			result = con.execute('insert into projects values(?,?)', (self.projectname, datetime.datetime.now(),))
			result = con.execute('select rowid, * from projects where name=?', (self.projectname,))
			row = result.fetchone()
			self.project_id = row[0]

		con.commit()
		con.close()

	def start(self, taskname=None):
		con = sqlite3.connect(self.database_path)
		if taskname:
			result = con.execute('select rowid, * from tasks where project=? and name=? and active=?', (self.project_id, taskname, True,))
		else:
			result = con.execute('select rowid, * from tasks where project=? and name is null and active=?', (self.project_id, True,))
		#See if they exist already, but for now lets just put them in.
		results = list()
		for row in result:
			t = Task(row[1], row[2], row[3], row[4], row[5], row[6])
			results.append(t)

		if len(results) > 0:
			print('There are %i active tasks with the same name, you should complete them before starting another.' % len(results))
		else:
			con.execute('insert into tasks(project, name, start, active, synced) values(?,?,?,?,?)', (
				self.project_id, taskname, datetime.datetime.now(), True, False))
			con.commit()
			con.close()

	def stop(self, taskname=None):
		if self.lastaction and self.lastaction['action'] == 'start':
			self.lastaction = dict(action='stop', 
									timestamp=datetime.datetime.now().isoformat(),
									taskname=taskname)

			self.action_count += 1
			self.actions[self.action_count] = self.lastaction
			self._save_config()
		else:
			print('It seems as though you weren\'t working on anything.')

if __name__ == '__main__':
	args = parser.parse_args()

	tt = TimeTracker(args.database, args.project)

	if args.action == 'start':
		tt.start(args.taskname)