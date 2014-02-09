import argparse
import json
import os
import datetime


parser = argparse.ArgumentParser(description='Keep track of tasks and time.')
parser.add_argument('action', help="start or stop tracking")
parser.add_argument('taskname', nargs='?')

parser.add_argument('--config', 
					help="Specify a path for config file, otherwise uses current working directory.")


class TimeTracker:
	def __init__(self, tt_file_path=None):
		self.path = os.getcwd()

		if tt_file_path:
			print(tt_file_path)
			self.tt_file_path = tt_file_path
			if os.path.exists(self.tt_file_path):
				self._load_config()
			else:
				self._load_defaults()
		if not tt_file_path:
			self.tt_file_path = os.path.join(self.path, '.tt')
			if os.path.exists(self.tt_file_path):
				self._load_config()
			else:
				self._load_defaults()

	def _load_defaults(self):
		self.projectname = os.path.basename(self.path)
		self.actions = list()
		self.lastaction = None
		self._save_config()

	def _load_config(self):
		with open(self.tt_file_path, 'r') as tt_file:
			tt_json = json.load(tt_file)
			self.projectname = tt_json['projectname']
			self.actions = tt_json['actions']
			self.lastaction = self.actions[-1]

	def _save_config(self):
		tt_obj = dict()
		tt_obj['projectname'] = self.projectname
		tt_obj['actions'] = self.actions
		tt_obj['lastaction'] = self.lastaction

		with open(self.tt_file_path, 'w') as tt_file:
			json.dump(tt_obj, tt_file, indent=4)

	def start(self, taskname=None):
		self.lastaction = dict(action='start',
								timestamp=datetime.datetime.now().isoformat(),
								taskname=taskname)

		self.actions.append(self.lastaction)
		self._save_config()

	def stop(self, taskname=None):
		if self.lastaction['action'] == 'start':
			print('rad')
		self.lastaction = dict(action='stop', 
								timestamp=datetime.datetime.now().isoformat(),
								taskname=taskname)
		self.actions.append(self.lastaction)
		self._save_config()


if __name__ == '__main__':
	args = parser.parse_args()
	tt = TimeTracker(args.config)
	
	if args.action == 'start':
		tt.start(args.taskname)
	if args.action == 'stop':
		tt.stop(args.taskname)