#Project Music Lyrics Catalog

#Description:
The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system.
In this sample project, the homepage displays all current categories along with the latest added items.

#Environment set up
1- Install Vagrant and the Virtual Machine following the instructions in this URL https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/348776022975460/lessons/3621198668/concepts/35960790720923
2- Make sure this line is in the Vagrantfile "config.vm.network "forwarded_port", guest: 5000, host: 5000"
3- Bring the virtual machine online and log into it
4- Unzip the contents of lyricscatalog.rar into a folder
5- cd into vagrant
6- cd into the folder where the files from lyricscatalog.zip were unzipped
7- from the virtual machine run "python lyricscatalog.py"
8- if you need to repopulate the database then delete lyricscatalog.db and run "python dbmodel.py" followed by "python lotsofsongs.py"

#Disclosure
The functions gconnect and gdisconnect inside lyricscatalog.py are reused from the code of lessons 3-10 and 3-11. 
Part of the code inside login.html is also reused from the code of lessons 3-10 and 3-11.
The rest of the code is completely original









