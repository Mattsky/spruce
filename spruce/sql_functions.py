# Spruce - a tool to help manage system software states.
# Copyright (C) 2017 Matt North

# This file is part of Spruce.

# Spruce is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Spruce is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Spruce.  If not, see <http://www.gnu.org/licenses/>.

import MySQLdb
import sys

# Requires mysqlclient (fork of MySQLdb - https://pypi.python.org/pypi/mysqlclient, 'pip3 install mysqlclient' works)
# Docs at https://mysqlclient.readthedocs.io/

def create_database(db_host, db_name, db_user, db_pass, db_root_user, db_root_pass):

    try:
        con = MySQLdb.connect(host=db_host, user=db_root_user, passwd=db_root_pass)

        cur = con.cursor()
        findquery="""SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='%s'""" % ( db_name )
        cur.execute(findquery)

        if cur.fetchone():
            print("Database exists - skipping")
        else:
            print("Creating database.")
            #cur2 = con.cursor()
            createquery="""CREATE DATABASE %s""" % (db_name)
            cur.execute(createquery)
            privquery="""GRANT ALL ON %s.* TO '%s' IDENTIFIED BY '%s'""" % ( db_name, db_user, db_pass )
            print(privquery)
            cur.execute(privquery)
            con.commit()

    except:

        print("Oh no!")

    finally:
        if con:
            con.close()

def ubuntu_create_installed_package_table(db_host, db_name, db_user, db_pass, host_name, package_list):

    try:
        con = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)

        cur = con.cursor()
        dropquery="""drop table if exists `%s_packages`""" % ( host_name )
        cur.execute(dropquery)
        print("Creating table.")
     
        createquery="""create table `%s_packages` (id INT NOT NULL AUTO_INCREMENT, package VARCHAR(60), currentver VARCHAR(60), PRIMARY KEY (id))""" % ( host_name )
        cur.execute(createquery)
        for x in package_list:
            updatequery="""INSERT INTO `%s_packages` (package, currentver ) VALUES ('%s', '%s' )""" % ( host_name, x[0], x[1])
            cur.execute(updatequery)
            con.commit()

    except:

        print("Oh no!")

    finally:
        if con:
            con.close()

def ubuntu_create_host_update_table(db_host, db_name, db_user, db_pass, host_name, update_list):

    try:
        con = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)

        cur = con.cursor()
        dropquery="""drop table if exists `%s_updates`""" % ( host_name )
        cur.execute(dropquery)
        print("Creating table.")
     
        createquery="""create table `%s_updates` (id INT NOT NULL AUTO_INCREMENT, package VARCHAR(40), currentver VARCHAR(60), newver VARCHAR(60), PRIMARY KEY (id))""" % ( host_name )
        cur.execute(createquery)
        for x in update_list:
            updatequery="""INSERT INTO `%s_updates` (package, currentver, newver ) VALUES ('%s', '%s', '%s')""" % ( host_name, x[0], x[1], x[2])
            cur.execute(updatequery)
            con.commit()

    except:

        print("Oh no!")

    finally:
        if con:
            con.close()

def ubuntu_get_available_host_updates(db_host, db_name, db_user, db_pass, host_name):

    try:
        con = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)

        cur = con.cursor()
        getquery="""select package from `%s_updates`""" % ( host_name )
        cur.execute(getquery)
        update_list = cur.fetchall() 
        # Return list of packages to be updated
        return update_list

    except:

        print("Oh no!")

    finally:
        if con:
            con.close()

def ubuntu_create_host_held_package_table(db_host, db_name, db_user, db_pass, host_name, held_packages):

    try:
        print(type(held_packages))
        con = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)

        cur = con.cursor()
        dropquery="""drop table if exists `%s_held`""" % ( host_name )
        cur.execute(dropquery)
        if held_packages is not None:
            print("Creating table.")
         
            createquery="""create table `%s_held` (id INT NOT NULL AUTO_INCREMENT, package VARCHAR(40), currentver VARCHAR(40), PRIMARY KEY (id))""" % ( host_name )
            cur.execute(createquery)
            for x in held_packages:
                print(x)
                updatequery="""INSERT INTO `%s_held` (package, currentver) VALUES ('%s', '%s')""" % ( host_name, x[0], x[1])
                cur.execute(updatequery)
                con.commit()

    except:

        print("Oh no!")

    finally:
        if con:
            con.close()

def centos7_create_installed_package_table(db_host, db_name, db_user, db_pass, host_name, package_list):

    try:
        con = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
        #['zlib', 'x86_64', '1.2.7-17.el7']

        cur = con.cursor()
        dropquery="""drop table if exists `%s_packages`""" % ( host_name )
        cur.execute(dropquery)
        print("Creating table.")
     
        createquery="""create table `%s_packages` (id INT NOT NULL AUTO_INCREMENT, package VARCHAR(60), arch VARCHAR(10), currentver VARCHAR(60), PRIMARY KEY (id))""" % ( host_name )
        cur.execute(createquery)
        for x in package_list:
            updatequery="""INSERT INTO `%s_packages` (package, arch, currentver ) VALUES ('%s', '%s', '%s' )""" % ( host_name, x[0], x[1], x[2])
            cur.execute(updatequery)
            con.commit()

    except:

        print("Oh no!")

    finally:
        if con:
            con.close()

def centos7_create_host_locked_package_table(db_host, db_name, db_user, db_pass, host_name, held_packages):

    try:
        print(type(held_packages))
        print(held_packages)
        con = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)

        cur = con.cursor()
        dropquery="""drop table if exists `%s_held`""" % ( host_name )
        cur.execute(dropquery)
        if held_packages is not None:
            print("Creating table.")
         
            createquery="""create table `%s_held` (id INT NOT NULL AUTO_INCREMENT, package VARCHAR(40), currentver VARCHAR(40), PRIMARY KEY(id))""" % ( host_name )
            cur.execute(createquery)
            for x in held_packages:
                print(x)
                updatequery="""INSERT INTO `%s_held` (package, currentver) VALUES ('%s', '%s')""" % ( host_name, x[0], x[1])
                cur.execute(updatequery)
                con.commit()

    except:

        print("Oh no!")

    finally:
        if con:
            con.close()

def centos7_create_host_update_table(db_host, db_name, db_user, db_pass, host_name, update_list):

    try:
        con = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)

        cur = con.cursor()
        print(host_name)
        dropquery="""drop table if exists `%s_updates`""" % ( host_name )
        cur.execute(dropquery)
        print("Creating table.")
        
        # Structure: package name, arch, update version, repo
        createquery="""create table `%s_updates` (id INT NOT NULL AUTO_INCREMENT, package VARCHAR(40), arch VARCHAR(10), newver VARCHAR(40), repo VARCHAR(40), PRIMARY KEY(id))""" % ( host_name )
        cur.execute(createquery)
        for x in update_list:
            print(x)
            updatequery="""INSERT INTO `%s_updates` (package, arch, newver, repo ) VALUES ('%s', '%s', '%s', '%s')""" % ( host_name, x[0], x[1], x[2], x[3])
            cur.execute(updatequery)
            con.commit()

    except:

        print("Oh no!")

    finally:
        if con:
            con.close()