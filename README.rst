TimeTracker
===========

TimeTracker (tt) is a python task management tool. Developed primarily out of my own needs as a consultant and a procrastinator.

Installation
============

Use pip to install TimeTracker into your virtualenv.

.. code-block:: bash

	$ pip install -e https://github.com/Ateoto/tt.git

Usage
=====

Lets track our time in a project!

.. code-block:: bash

	$ tt start "Working on easing installation"

That's it, TimeTracker is now tracking how long it's taken you to fix this broken install process.

Ok, I've fixed the install process (just for the sake of example).
Commit the changes to your repo and then:

.. code-block:: bash
	
	$ tt stop "Working on easing installation"
	$ Working on easing installation completed. Elapsed Time: 20 minutes

You can also see a list of active tasks.

.. code-block:: bash

	$ tt list
	Open Tasks:
	===========
	[None] (Elapsed time: 1 hours, 23 minutes)
	[Working on list command.] (Elapsed time: 36 minutes)
	[Pretty Elapsed Time.] (Elapsed time: 24 minutes)

There is a lot more to come.

Features
========

 - Uses an sqlite database to keep track of active and closed tasks.
 - Simple implementation.
 - Simple API.
 - Coming Soon: Integration with a Django project to allow fine grained views on time management.