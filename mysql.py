#! /usr/bin/python

import MySQLdb

def connect(host, user, password, db, charset, use_unicode):
    """
        Opens database connection to the *host* for the *user* with the *password* for the database named *db*. Returns connection object in case of succesful connection.
    """

    try:
        conn=MySQLdb.connect(host,user,password,db,charset=charset,use_unicode=use_unicode)
        return conn
    except MySQLdb.Error, e:
        print "ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1])

def write(sql, conn, cursor):
    """
        Perform insert and update operations on the database.

        **Parameters**
            sql : Query to execute.
            conn: connection object.
            cursor : Cursor object.
    """

    try:
        cursor.execute(sql)
        conn.commit()
    except MySQLdb.ProgrammingError, e:
        print "ERROR %d IN WRITE OPERATION: %s" % (e.args[0], e.args[1])
        print "LAST QUERY WAS: %s" %sql

def read(sql,cursor):
    """
        Perform read operations on the database.

        **Parameters**
            sql : Query to execute.
            cursor : Cursor object.
    """
    try:
        cursor.execute(sql)
        result=cursor.fetchall()
        return result
    except MySQLdb.ProgrammingError, e:
        print "ERROR %d IN READ OPERATION: %s" % (e.args[0], e.args[1])
        print "LAST QUERY WAS: %s" %sql
