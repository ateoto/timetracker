TimeTracker
===========

TimeTracker (tt) is a python task management tool. Developed primarily out of my own needs as a consultant and a procrastinator.

Installation
============

Use pip to install TimeTracker into your virtualenv.

.. code-block:: bash

	$ pip install -e https://github.com/Ateoto/timetracker.git

Usage
=====

Lets track our time in a project!

.. code-block:: bash

	$ tt start "Working on easing installation"

That's it, TimeTracker is now tracking how long it's taken you to fix this broken install process.

Ok, I've fixed the install process (just for the sake of example).
Commit the changes to your repo and then:

.. code-block:: bash
	
	$ tt stop
	$ Working on easing installation completed. Elapsed Time: 20 minutes

You can also see a list of active tasks.

.. code-block:: bash

	$ tt status
	New task (0 minutes)
	Old task (2 minutes) [Paused]


There is a special case for pausing tasks, it flags the task in the database and the program will ask if you'd like to continue it after you stop your current task. TimeTracker will prompt you to pause active tasks if you try to start a new task with another task open. You can also manually pause a task.

.. code-block:: bash

	$ tt status
	Current task (10 minutes)
	$ tt pause "Current task"
	Paused Current task

There is a lot more to come.

Tests
=====

This is still a work in progress, but it is a top priority for me.

.. code-block:: bash

	$ git clone https://github.com/Ateoto/timetracker.git
	$ cd timetracker
	$ python -m unittest discover


Features
========

 - Uses an sqlite database to keep track of active and closed tasks.
 - Simple implementation.
 - Simple API.
 - Coming Soon: Integration with a Django project to allow fine grained views on time management.