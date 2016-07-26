
#Tournament : SwissPairing

This project implements a swiss tournament. It creates database and tables related to a tournament, simulate insertion, deletion into tables. 

#Technologies
- Python
- SQL

#Software Requirement
- install python
- install git
- install VirtualBox
- install Vagrant

#Installation
- clone this repo
- use git command line to move to the clone folder /fullstack-nano-degree-vm/vagrant
- type <code>vagrant up</code> to launch the vagrant virtual machine
- type <code>vagrant ssh</code> to connect
- type <code>cd tournament</code>
- type <code>createdb tournament</code> to create the tournament database
- type <code>psql tournament</code> to connect to the database
- type <code> -i tournament.sql </code> to execute the tournament sql file and exit with <code>\q</code>
- type <code> python tournament_test.py </code> to launch the project
