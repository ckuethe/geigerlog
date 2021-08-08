#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gsup_sql.py - GeigerLog commands to handle sqlite3 databases

include in programs with:
    include gsup_sql
"""

###############################################################################
#    This file is part of GeigerLog.
#
#    GeigerLog is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GeigerLog is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GeigerLog.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
__credits__         = [""]
__license__         = "GPL3"

from   gsup_utils       import *


def DB_getLocaltime():
    """gets the localtime as both Julianday as well as timetag, like:
    res: (2458512.928904213, '2019-01-29 10:17:37') """

    sql = "select julianday('NOW', 'localtime'), DateTime('NOW', 'localtime')"
    xsel = gglobs.currentConn.execute(sql)
    res = xsel.fetchone()
    #print("DB_getLocaltime: sql: {}, res:".format(sql), res)

    return res[0], res[1]


def DB_JulianToDate(juliandate):
    """convert Julian=2458403.02342593 to datetime=2018-10-11 12:33:44 """

    sql = "select DateTime({})".format(juliandate)
    xsel = gglobs.currentConn.execute(sql)
    res = xsel.fetchone()[0]
    #print("DB_JulianToDate swl: {}, res:".format(sql), res)

    return res


def DB_DateToJulian(ddate):
    """Convert "2018-10-11 12:33:44"  to Julian=2458403.10675926,
    or         "NOW"                  to Julian=2458500.15535483 """

    sql = "select julianday('{}')".format(ddate)
    xsel = gglobs.currentConn.execute(sql)
    res = xsel.fetchone()[0]
    print("DB_JulianToDate swl: {}, res:".format(sql), res)

    return res


def DB_GetFilepathFromDB(DB_Connection):
    """returns the filename with path used for this database"""

    fncname = "DB_GetFilepathFromDB: "
    dprint(fncname + "DB_Connection: ", DB_Connection)

    path = None
    pmlist = DB_Connection.execute('PRAGMA database_list')
    for id_, name, path in pmlist:
        dprint(fncname + "id_, name, path:", id_, name, path)
        if name == 'main' :
            break

    dprint(fncname + "path:", path)

    return path


def DB_closeDatabase(DBtype):
    """Close the database.
    Note: any changes not committed will be lost!
    """
    fncname = "DB_closeDatabase: "
    vprint(fncname + "Closing database: '{}'".format(DBtype))
    setDebugIndent(1)

    if      DBtype == "Log": DB_Connection = gglobs.logConn
    else:                    DB_Connection = gglobs.hisConn

    if DB_Connection == None:
        wprint(fncname + "Database is not open")
    else:
        try:
            DB_Connection.close()
            wprint(fncname +  "Closing done")
        except Exception as e:
            srcinfo = fncname + "Exception: connection is: {}".format(DB_Connection)
            exceptPrint(e, srcinfo)

    setDebugIndent(0)


def DB_deleteDatabase(DBtype, DB_FilePath):
    """Try to close database at DB_Connection, then delete database file at DB_FilePath"""
    """DBtype = "Log" or "His" """

    fncname = "DB_deleteDatabase: "
    dprint(fncname + "Deleting {} DB file: '{}'".format(DBtype, DB_FilePath))

    DB_closeDatabase  (DBtype)            # try to close DB

    try:    os.remove (DB_FilePath)       # try to remove DB file
    except: pass


def DB_openDatabase(DB_Connection, DB_FilePath):
    """Open the database"""

    fncname = "DB_openDatabase: "
    dprint(fncname + "DBpath: '{}'".format(DB_FilePath))
    setDebugIndent(1)

    needToCreateDB = False

    if os.access(DB_FilePath, os.W_OK):
        dprint(fncname + "Database file found")
        DB_Connection = sqlite3.connect(DB_FilePath, isolation_level="EXCLUSIVE")

        # find number of tables in file
        res     = DB_Connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables  = res.fetchall()
        ntables = len(tables)

        # find number of views in file
        res     = DB_Connection.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;")
        views   = res.fetchall()
        nviews  = len(views)

        if ntables == 0 or nviews == 0:
            needToCreateDB = True
            vprint(fncname + "Database file is missing structure")
        else:
            # find number of rows in table data
            res    = DB_Connection.execute("SELECT count(*) FROM  data")
            rows   = res.fetchone()
            dnrows = rows[0]
            res    = DB_Connection.execute("SELECT count(*) FROM  comments")
            rows   = res.fetchone()
            cnrows = rows[0]
            # note: format syntax: {:n} --> '.' as separator, {:,} --> ',' as separator
            vprint(fncname + "Database has {} tables, {} views, with {:n} rows in table data, {:n} rows in table comments".format(ntables, nviews, dnrows, cnrows))

        needToCreateDB = True # will always update the DB structure to include any new tables

    else:
        vprint(fncname + "DB file not found; creating DB with path: '{}'".format(DB_FilePath))
        DB_Connection = sqlite3.connect(DB_FilePath, isolation_level="EXCLUSIVE")
        needToCreateDB = True

    if needToCreateDB: DB_createStructure(DB_Connection)

    gglobs.currentConn      = DB_Connection

    setDebugIndent(0)

    return DB_Connection


def DB_commit(DB_Connection):
    """Commit all changes on connection DB_Connection"""

    try:
        DB_Connection.commit()
    except Exception as e:
        srcinfo = "DB_commit: commit"
        exceptPrint(e, srcinfo)


def DB_createStructure(DB_Connection):
    """Create the database with tables and views"""

    fncname = "DB_createStructure: "

    dprint(fncname)
    setDebugIndent(1)

    # execute all sql to create database structure
    for sql in sqlCreate:
        try:
            DB_Connection.execute(sql)
            sqls = sql.strip()
            vprint(fncname + "sql done: ", sqls[:sqls.find("\n")], "...")
        except Exception as e:
            if not ("already exists" in str(e)):
                srcinfo = fncname
                exceptPrint(e, srcinfo)
    dprint(fncname + "complete")

    DB_commit(DB_Connection)
    setDebugIndent(0)


def DB_insertData(DB_Connection, datalist):
    """Insert many rows of data into the table data"""

    fncname = "DB_insertData: "

    sql = sqlInsertData
    #wprint(fncname + "SQL:", sql, ", Data: ", datalist[0:10])

    try:
        DB_Connection.executemany(sql, datalist)
    except Exception as e:
        srcinfo = fncname + "Exception:" + sql
        exceptPrint(e, srcinfo)

    DB_commit(DB_Connection)


def DB_insertParse(DB_Connection, datalist):
    """Insert many rows of data into the table parse
    ATTENTION: datalist MUST be a list of lists to 'executemany' !!!"""

    fncname = "DB_insertParse: "

    sql = sqlInsertParse
    #wprint(fncname + "SQL:", sql, ", Data: ", datalist[0:10])

    try:
        DB_Connection.executemany(sql, datalist)
    except Exception as e:
        srcinfo = fncname + "Exception: " + sql
        exceptPrint(e, srcinfo)

    DB_commit(DB_Connection)


def DB_insertComments(DB_Connection, datalist):
    """Insert many rows of data into the table comments
    ATTENTION: datalist MUST be a list of lists to 'executemany' !!!"""

    fncname = "DB_insertComments: "

    sql = sqlInsertComments
    #wprint(fncname + "SQL:", sql, ", Data: ", datalist[0:10])

    try:
        DB_Connection.executemany(sql, datalist)
    except Exception as e:
        srcinfo = fncname + "Exception: " + sql
        exceptPrint(e, srcinfo)

    DB_commit(DB_Connection)


def DB_insertBin(DB_Connection, binblob):
    """Insert a row of data into the table bin - should be the only row!"""

    fncname = "DB_insertBin: "

    sql = sqlInsertBin
    #wprint(fncname + "SQL:", sql, ", Data: ", binblob[0:10])

    try:
        DB_Connection.execute(sql, (binblob,))
    except Exception as e:
        srcinfo = fncname + "Exception: " + sql
        exceptPrint(e, srcinfo)

    DB_commit(DB_Connection)


def DB_insertDevice(DB_Connection, ddatetime, dname):
    """Insert a row of data into the table bin - should be the only row!"""

    fncname = "DB_insertDevice: "

    sql = sqlInsertDevice
    #wprint(fncname + "SQL:", sql, ", Data: ", ddatetime, dname)

    try:
        DB_Connection.execute(sql, (ddatetime, dname))
    except Exception as e:
        srcinfo = fncname + "Exception: " + sql
        exceptPrint(e, srcinfo)

    DB_commit(DB_Connection)



def DB_readData(DB_Connection, sql, limit=0):
    """Read the data from the database data table
    if limit=0, the std sql is called, otherwise the lower or upper LIMIT limit"""

    res     = DB_Connection.execute(sql)
    rows    = res.fetchall()
    if limit > 0:    rows   = rows[0:limit] + rows[-limit:]
    #print("rows:", rows)

    ddd = [x[1:2][0] for x in rows]

    return ddd


def DB_readComments(DB_Connection):
    """Read the data from the database table comments"""

    sql =  """
            select
                cjulianday as julianday,
                printf("#%8s, %19s, %s",
                        ctype               ,
                        datetime(cjulianday),
                        cinfo
                      ) as commentstr,
                ctype
            from comments
            order by julianday asc, rowid asc
            """

    res     = DB_Connection.execute(sql)
    rows    = res.fetchall()
    #print("rows:", nrows, "\n", rows)

    ddd     = [x[1:2][0] for x in rows] # make a list of only the commentstr

    return ddd


def DB_readBinblob(DB_Connection):
    """Read the data from the database table bin"""

    sql = """
            select
                bblob
            from bin
            """

    res     = DB_Connection.execute(sql) # res is a sqlite3.Cursor object
    blob    = res.fetchone()
    if blob == None:
        return None
    else:
        return blob[0]


def DB_readParse(DB_Connection):
    """Read the data from the database table parse
    return: True if at least 1 parse record, False if no records
    """

    sql = """
            select
                pindex,
                pinfo
            from parse
          """

    res     = DB_Connection.execute(sql) # res is a sqlite3.Cursor object
    parse0  = res.fetchone() # 1st record only

    if parse0 == None:  return False
    else:               return True


def DB_readDevice(DB_Connection):
    """Read the data from the database table device"""

    sql = """
            select
                ddatetime,
                dname
            from device
            """

    res     = DB_Connection.execute(sql)
    rows    = res.fetchone()
    #print("DB_readDevice: fetched 1 rows  with items: ", len(rows), rows)

    return rows


def DB_readLogcycle(DB_Connection):
    """Read the data from the database table logcycle"""

    sql = """
            select
                lcycle
            from logcycle
          """

    res     = DB_Connection.execute(sql) # res is a sqlite3.Cursor object
    parse0  = res.fetchone() # 1st record only

    if parse0 == None:
        return None
    else:
        return parse0[0]


def DB_insertLogcycle(DB_Connection, value):
    """Insert the value into the database table logcycle"""

    fncname = "DB_insertLogcycle: "
    sql = """INSERT INTO logcycle (lcycle)  VALUES (?)"""

    vprint(fncname + "SQL:", sql, ", Data: ", value)

    try:
        DB_Connection.execute(sql, (value,))
    except Exception as e:
        srcinfo = fncname + "Exception: " + sql
        exceptPrint(e, srcinfo)

    DB_commit(DB_Connection)


def DB_updateLogcycle(DB_Connection, value):
    """Update database table logcycle in rowid=1 with value"""

    fncname = "DB_updateLogcycle: "
    sql = """UPDATE logcycle SET lcycle=(?) where ROWID=1"""

    vprint(fncname + "SQL:", sql, ", Data: ", value)

    try:
        DB_Connection.execute(sql, (value,))
    except Exception as e:
        srcinfo = fncname + "Exception: " + sql
        exceptPrint(e, srcinfo)

    DB_commit(DB_Connection)


def createFFmapFromDB():
    """Read data from table bin as blob and print map of FFs into notePad"""

    if gglobs.hisConn == None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    start = time.time()

    fprint(header("Show History Binary Data as FF Map"))
    fprint("from: {}\n".format(gglobs.hisDBPath))

    hist    = DB_readBinblob(gglobs.hisConn)
    #print("createFFmapFromDB: hist:", hist)
    if hist == None:
        efprint("No binary data found in this database")
        return

    setBusyCursor()

    lenLine   = 1024
    lenChunk  = 16
    lenHist   = len(hist)
    markline  = "Occurence of 0xFF values in History binary data is marked with 'X'\n"
    lstlines  = markline
    lstlines += "1 printed character maps a chunk of 16 bytes of data\n"
    lstlines += "Byte No|" + "_______|" * 8 + "\n"
    counter   = 0
    batch     = 100
    for i in range(0, lenHist, lenLine):
        if counter == batch:
            fprint(lstlines[:-1])
            lstlines = ""
            counter  = 0

        lstline ="{:7d}|".format(i)
        for j in range(0, lenLine, lenChunk):
            l = i + j
            if l >= lenHist: break
            if 255 in hist[l:l + lenChunk]:  s = "X"
            else:                            s = "."
            lstline += s

        lstlines += lstline + "\n"
        counter  += 1

    fprint(lstlines)
    vprint("timing 16b per char chunks: {:7.2f}ms".format((time.time() -start)*1000))

    setNormalCursor()

### flag!!!!!!!!!!!!!!!!!!!11

def createParseFromDB(lmax=12, full=True):
    """Read the data from the database data table include comments and parse comments """

    if gglobs.hisConn == None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    fprint(header("Show History Data with Parse Comments"))
    fprint("from: {}\n".format(gglobs.hisDBPath))

    if not DB_readParse(gglobs.hisConn):
        efprint("No Parse Comments data found in this database")
        return
    else:
        print("createParseFromDB: parse records were found")

    setBusyCursor()

    sql = """
            select
                julianday,
                printf(" %8s, %19s, %6s, %6s, %6s, %6s, %6s, %6s, %s",
                        data.dindex            ,
                        datetime(julianday)    ,
                        ifnull(cpm,         ""),
                        ifnull(cps,         ""),
                        ifnull(cpm1st,      ""),
                        ifnull(cps1st,      ""),
                        ifnull(cpm2nd,      ""),
                        ifnull(cps2nd,      ""),
                        ifnull(parse.pinfo, "")
                      ) as datastr,
                data.dindex
            from data

            LEFT JOIN parse
            ON  data.dindex = parse.pindex

            union

            select
                cjulianday as julianday,
                printf("#%8s, %19s, %s",
                        ctype               ,
                        datetime(cjulianday),
                        cinfo
                      ) as commentstr,
                ctype
            from comments
            order by julianday asc, data.dindex asc
            """

    res     = gglobs.hisConn.execute(sql)
    data    = res.fetchall()
    print("createParseFromDB: sql:", sql, "\ndata:", len(data), "data:\n", data)

    ruler  = "## Index,            DateTime,    CPM,    CPS, CPM1st, CPS1st, CPM2nd, CPS2nd, ParseInfo"
    fprint(ruler)
    counter     = 0
    batch       = 100
    printstring = ""
    gglobs.stopPrinting = False

    if full:
        for a in data:
            #print("createParseFromDB: a[1]:", a[1])
            if counter == batch:
                fprint(printstring[:-1])
                printstring = ""
                counter     = 0
            printstring += a[1] + "\n"
            counter     += 1
            if gglobs.stopPrinting: break
        gglobs.stopPrinting = False
    else:
        for a in data[:+lmax]: fprint(a[1])
        fprint('...')
        for a in data[-lmax:]: fprint(a[1])

    fprint(printstring[:-1])
    fprint(ruler)

    setNormalCursor()


def createLstFromDB(*args, lmax=12, full=True):
    """create Binary Data in Human-Readable Form from the database table bin"""

    #vprint("createLstFromDB:  lmax={}, full={}".format(lmax, full))

    if gglobs.hisConn == None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    if full: addh = ""          # all lines
    else:    addh = " Excerpt"  # excerpt only
    fprint(header("Show History Binary Data in Human Readable Form" + addh))
    fprint("from: {}\n".format(gglobs.hisDBPath))

    hist    = DB_readBinblob(gglobs.hisConn)
    #print("createLstFromDB: hist:", hist)
    if hist == None:
        efprint("No binary data found in this database")
        return

    setBusyCursor()

    histlen     = len(hist)                  # Total length; could be any length e.g. when read from file
    histRC      = hist.rstrip(b'\xFF')       # after right-clip FF (removal of all trailing 0xff)
    histRClen   = len(histRC)                # total byte count
    ppagesize   = 1024                          # for the breaks in printing
    data_origin = "Download Date: {} from device {}".format(* DB_readDevice(gglobs.hisConn))

    # header
    lstlines    = "#History Download - Binary Data in Human-Readable Form\n"
    lstlines   += "#{}\n".format(data_origin)
    lstlines   += "#Format: bytes_index[hex]=bytes_index[dec] : value[hex]=value[dec] |\n"

    # This takes the full hist data clipped for FF, independent of the
    # memory setting of the currently selected counter
    for i in range(0, histRClen, ppagesize):
        for j in range(0, ppagesize, 4):
            lstline =""
            for k in range(0, 4):
                if j + k >= ppagesize:   break
                l  = i + j + k
                if l >= histRClen:       break
                lstline += "{:04x}={:<5d}:{:02x}={:<3d}|".format(l, l, histRC[l], histRC[l])
            lstlines += lstline[:-1] + "\n"
            if l >= histRClen:           break

        lstlines += "Reading Page {} of size {} bytes complete; next address: 0x{:04x}={:5d} {}\n".format(i/ppagesize, ppagesize, i+ppagesize, i+ppagesize, "-" * 6)
        #print "(l +1)", (l+1), "(l +1) % 4096", (l+1) % 4096
        if (l + 1) % 4096 == 0 :
            lstlines += "Reading Page {} of size {} Bytes complete {}\n".format(i/4096, 4096, "-" * 35)
        if l >= histRClen:               break

    if histRClen < histlen:
        lstlines += "Remaining {} Bytes to the end of history (size:{}) are all ff\n".format(histlen -histRClen, histlen)
    else:
        lstlines += "End of history reached\n"

    listlstlines = lstlines.split('\n')[:-1]
    if full:
        for a in listlstlines:
            fprint(a)
            if gglobs.stopPrinting: break

    else: #excerpt only
        for a in listlstlines[:+lmax]: fprint(a)
        fprint('...')
        for a in listlstlines[-lmax:]: fprint(a)
    fprint("")

    setNormalCursor()


###############################################################################

sqlGetLogUnionAsString =   """
                select
                    julianday,
                    printf(" %8s, %19s, %7s, %7s, %7s, %7s, %7s, %7s, %7s, %7s, %7s, %7s",
                            dindex            ,
                            datetime(julianday),
                            ifnull(cpm,     ""),
                            ifnull(cps,     ""),
                            ifnull(cpm1st,  ""),
                            ifnull(cps1st,  ""),
                            ifnull(cpm2nd,  ""),
                            ifnull(cps2nd,  ""),
                            ifnull(T,       ""),
                            ifnull(P,       ""),
                            ifnull(H,       ""),
                            ifnull(X,       "")
                          ) as datastr,
                    dindex
                from data

                union

                select
                    cjulianday as julianday,
                    printf("#%8s, %19s, %s",
                            ctype               ,
                            datetime(cjulianday),
                            cinfo
                          ) as commentstr,
                    ctype
                from comments

                order by julianday asc, dindex asc
                """

# sql INSERT commands
# NOTE: when the argument to julianday is already julianday, sqlite does not change it!
#sqlInsertData       = """INSERT INTO data       (dindex, Julianday, cpm, cps, cpm1st, cps1st, cpm2nd, cps2nd, t, p, h, r) VALUES (?,julianday(?,?),?,?,?,?,?,?,?,?,?,?)"""
sqlInsertData       = """INSERT INTO data       (dindex, Julianday, cpm, cps, cpm1st, cps1st, cpm2nd, cps2nd, cpm3rd, cps3rd, t, p, h, x) VALUES (?,julianday(?,?),?,?,?,?,?,?,?,?,?,?,?,?)"""
sqlInsertComments   = """INSERT INTO comments   (ctype, cJulianday, cinfo)  VALUES (?, julianday(?, ?), ?)"""
sqlInsertParse      = """INSERT INTO parse      (pindex, pinfo)             VALUES (?, ?)"""
sqlInsertDevice     = """INSERT INTO device     (ddatetime, dname)          VALUES (?, ?)"""
sqlInsertBin        = """INSERT INTO bin        (bblob)                     VALUES (?)"""


# assemble all the commands needed to make the database structure as a list,
# and any commands needed to run after openeing/creating the db
sqlCreate = []

# make table data
# Index, DateTime, CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  Temp, Press, Humid, RMCPM
sqlCreate.append('''
        CREATE TABLE data
             (
              dindex    INTEGER,
              Julianday REAL,
              CPM       REAL,
              CPS       REAL,
              CPM1st    REAL,
              CPS1st    REAL,
              CPM2nd    REAL,
              CPS2nd    REAL,
              CPM3rd    REAL,
              CPS3rd    REAL,
              T         REAL,
              P         REAL,
              H         REAL,
              X         REAL
             )
        ''')

# make table comments
# ctype, DateTime, cinfo
sqlCreate.append('''
        CREATE TABLE comments
             (
              ctype      INTEGER,
              cJulianday REAL,
              cinfo      TEXT
             )
        ''')

# make table parse
# dindex (for joining with data table), pinfo (the parse text)
sqlCreate.append('''
        CREATE TABLE parse
             (
              pindex     INTEGER,
              pinfo      TEXT
             )
        ''')


# make table bin
# storing the binary data as a blob
sqlCreate.append('''
        CREATE TABLE bin
             (
              bblob     BLOB
             )
        ''')

# make table device
# storing the device name and the download datetime string
sqlCreate.append('''
    CREATE TABLE device
         (
          ddatetime  TEXT,
          dname      TEXT
         )
    ''')

# make table logcycle
# storing the logcycle in sec
sqlCreate.append('''
    CREATE TABLE logcycle
         (
          lcycle    FLOAT
         )
    ''')

sqlCreate.append("""CREATE VIEW ViewData     AS Select ROWID, Datetime(Julianday),  * from data     order by  Julianday, dindex""")
sqlCreate.append("""CREATE VIEW ViewComments AS Select ROWID, Datetime(cJulianday), * from comments order by cJulianday, ctype """)
sqlCreate.append("""CREATE VIEW ViewUnion    AS {}""".format(sqlGetLogUnionAsString))


def getShowCompactDataSql(varchckd):
    """gets unioned data & comments, but only for variables existing in DB"""

    sqlprintftmplt = """
            printf(" %8s, %19s{}{}{}{}{}{}{}{}{}{}{}{}",
                   dindex,
                   datetime(julianday)
                   {}{}{}{}{}{}{}{}
                   {}{}{}{}
                  )
            """                             # needs a filler with 24 places

    ruler  = "#>  Index,            DateTime"
    filler = [""] * 24
    for i, vname in enumerate(gglobs.varsBook):
        #print("i:, vname: ", i, vname)
        if varchckd[vname]:
            #print("varchecked: i:, vname: ", i, vname)
            filler [i]    = ", %7s"
            filler [i+12] = """, ifnull({}, "")""".format(vname)
            ruler        += ", {:>7s}".format(vname)
        else:
            #print("NOT varchecked: i:, vname: ", i, vname)
            filler [i]    = ""
            filler [i+12] = ""

    sqlprintft = sqlprintftmplt.format(*filler)
    #print("sqlprintft:", sqlprintft)

    OLDsql =   """
            select
                julianday,
                {}
                as datastr,
                dindex,
                rowid
            from data

            union

            select
                cjulianday as julianday,
                printf("#%8s, %19s, %s",
                        ctype               ,
                        datetime(cjulianday),
                        cinfo
                      ) as commentstr,
                ctype,
                rowid
            from comments

            order by julianday asc, rowid asc
            """.format(sqlprintft) # order by julianday asc, dindex asc, rowid asc : not good

    sql =   """
            select
                julianday,
                {}
                as datastr,
                dindex,
                rowid
            from data

            union

            select
                cjulianday as julianday,
                printf("#%8s, %19s, %s",
                        ctype               ,
                        datetime(cjulianday),
                        cinfo
                      ) as commentstr,
                ctype,
                rowid
            from comments

            order by julianday asc, dindex asc, rowid asc
            """.format(sqlprintft) # order by julianday asc, dindex asc, rowid asc : not good wieso not good? geht doch????


    #print("sql:", sql)

    return sql, ruler


def getDataFromDatabase():
    """
    read the data from database
    and create data array with timestamp, CPM, CPS, etc
    """

    fncname = "getDataFromDatabase: "

    dprint(fncname)
    setDebugIndent(1)

    start = time.time()

    nrows           = None                           # set later by DB call
    ncols           = gglobs.datacolsDefault
    localvarchecked = gglobs.varcheckedCurrent.copy()

    sql = """
        SELECT
            Julianday - {} as jday,
            CPM,
            CPS,
            CPM1st,
            CPS1st,
            CPM2nd,
            CPS2nd,
            CPM3rd,
            CPS3rd,
            T,
            P,
            H,
            X
        FROM data
        WHERE Julianday IS NOT NULL
        ORDER BY jday
         """.format(gglobs.JULIAN111)

# get the db rows
    # as a list of tuples:
    # [(737062.8293287037, 14, 0, None, None, None, None, None, None, None, None),
    #  (737062.8293402777, 14, 0, None, None, None, None, None, None, None, None),
    #  (737062.8293518517, 14 ...
    # will crash if a column is not defined
    try:
        start3  = time.time()
        res     = gglobs.currentConn.execute(sql)
        rows    = res.fetchall()
        nrows   = len(rows)
        vprint(fncname +"{:8.2f}ms sql call, " .format((time.time() - start3) * 1000))
    #    self.toolPrintArrayInfo("rows", rows)
    except Exception as e:
        edprint(fncname + "get the db rows: Exception executing SQL: ", e, debug=True)
        edprint("SQL command: ", sql, debug=True)
        efprint("ERROR trying to read database: ", e)
        setDebugIndent(0)
        return np.empty([0, 0]), localvarchecked


# convert db rows to np array
    # np_rows is a type: <class 'numpy.ndarray'>, a ndarray of ndarrays, like:
    # [[737058.5991640585 17 0 ... 1024.68 32.0 9]
    #  [737058.5991872079 17 0 ... None None None]
    #  [737058.5992103536 17 0 ... None None None]
    start4 = time.time()
    np_rows = np.asarray(rows)
    vprint(fncname + "{:8.2f}ms convert db rows to np.asarray" .format((time.time() - start4) * 1000))
#    self.toolPrintArrayInfo("np_rows", np_rows)

#   create dataarray value by value, check for being "floatable"
    # dataArray is a type <class 'numpy.ndarray'>
    # this converts the None to nan
    # [[7.37058599e+05 1.70000000e+01 0.00000000e+00 ... 1.02468000e+03  3.20000000e+01 9.00000000e+00]
    #  [7.37058599e+05 1.70000000e+01 0.00000000e+00 ...            nan             nan            nan]
    #  [7.37058599e+05 1.70000000e+01 0.00000000e+00 ...
    start5      = time.time()
    dataArray   = np.empty([nrows, ncols])
    if nrows > 0:    # do it only when data are in the database;  otherwise ???
        for row in range(0, nrows):              # rows
            for col in range(0, ncols):          # columns
                try:
                    if np_rows[row, col] != '': dataArray [row, col] = np_rows[row, col]
                    else:                       dataArray [row, col] = gglobs.NAN
                    #dataArray [row, col] = np_rows[row, col]
                except Exception as e:
                    #print("np_rows[row, col]: '{}'".format(np_rows[row, col]), e)
                    dataArray[row, col] = gglobs.NAN # "ValueError: cannot convert float NaN to integer"
                    dprint(fncname + "create dataarray: Exception: row={}, col={} ".format(row, col), e)


# Check the dataarray for columns having ONLY nan values. Block those
# column from being selectable in combobox and showing in graph
    start6 = time.time()
    # all except DateTime set to true if at least one entry is not nan
    for i, a in enumerate(gglobs.varsBook):
        if not np.isnan(dataArray[:, i + 1]).all():
            #print("i:", i, a, "has data")
            localvarchecked [a] = True
        else:
            #print("i:", i, a, "has only nan data")
            localvarchecked [a] = False
    vprint(fncname + "{:8.2f}ms for nan checking, " .format((time.time() - start6) * 1000))

# Clean up
    dprint(fncname + "{:8.2f}ms total for {} records with {} values each".format((time.time() - start) * 1000, nrows, ncols))

    setDebugIndent(0)

    return dataArray, localvarchecked


def toolPrintArrayInfo(name, array):
    """tool for devel for some array properties"""

    print("\nArrayname: " + name + ": ")
    print("rows type:   ", type(array))
    print("len(rows):   ", len(array))
    print("all rows:\n",   array)
    print()
    print("rows[0] type:", type(array[0]))
    print("len(rows[0]):", len(array[0]))
    print("all rows[0]:\n", array[0])
    for i in range(len(array[0])):
        print("{}[0][{}]: {}, type:{}".format(name, i, array[0][i], type(array[0][i])))
    print("------------------------------------------------")



def saveData(dataSource=None, full=True):
    """Save Log or His Data to file as CSV. dataSource can be 'Log' or 'His'"""

    #print("saveData: dataSource, full: ", dataSource, full)

    if dataSource == "Log": connection  = gglobs.logConn
    else:                   connection  = gglobs.hisConn #  dataSource == "His"

    if connection == None:
        showStatusMessage("No data available")
        return

# dataSource == "Log"
    if dataSource == "Log":
        dtype       = "Log"
        dbpath      = gglobs.logDBPath
        #~csvfilename = dbpath + ".log"
        csvfilename = dbpath + ".csv"
        varchecked  = gglobs.varcheckedLog

# dataSource == "His"
    else:
        dtype       = "History"
        dbpath      = gglobs.hisDBPath
        #~csvfilename = dbpath + ".his"
        csvfilename = dbpath + ".csv"
        varchecked  = gglobs.varcheckedHis

    setBusyCursor()

    fprint(header("Saving {} Data as CSV File".format(dtype)))
    fprint("from: {}".format(dbpath))
    fprint("into: {}".format(csvfilename))

    #print("showLogData: varcheckedLog: ", gglobs.varcheckedLog)
    sql, ruler = getShowCompactDataSql(varchecked)

    writeFileW(csvfilename, "") # delete and recreate file
    data = DB_readData(connection, sql, limit=0)
    for a in data: writeFileA(csvfilename, a)

    setNormalCursor()


def saveRepairData(dataSource=None, full=True):
    """Save Log or His Data to file as CSV. dataSource can be 'Log' or 'His'"""
    # was intended to repair a History recorded with Clock-broken GMC500+,
    # but does not work sufficiently well!

    def _convertUnixtimeToDateTime(unixtime):
        """convert a Unix time in sec into datetime like: 2020-05-10 11:48:50"""
        return datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')

    #print("saveData: dataSource, full: ", dataSource, full)

    if dataSource == "Log": connection  = gglobs.logConn
    else:                   connection  = gglobs.hisConn #  dataSource == "His"

    if connection == None:
        showStatusMessage("No data available")
        return

    if dataSource == "Log":
        dtype       = "Log"
        dbpath      = gglobs.logDBPath
        csvfilename = dbpath + ".log"
        varchecked  = gglobs.varcheckedLog

    else:                                   # dataSource == "His"
        dtype       = "History"
        dbpath      = gglobs.hisDBPath
        csvfilename = dbpath + ".his"
        varchecked  = gglobs.varcheckedHis

    setBusyCursor()

    fprint(header("Saving {} Data as CSV File".format(dtype)))
    fprint("from: {}".format(dbpath))
    fprint("into: {}".format(csvfilename))

    print("showLogData: varcheckedLog: ", gglobs.varcheckedLog)
    sql, ruler = getShowCompactDataSql(varchecked)

    writeFileW(csvfilename, "") # delete and recreate file
    data = DB_readData(connection, sql, limit=0)
    for a in data[:30]:
        print("a: ", a) # a has no LF
        #~writeFileA(csvfilename, a)
    print("...")
    for a in data[-30:]:
        print("a: ", a) # a has no LF
        #~writeFileA(csvfilename, a)

    print("\n\n")
    # unix: 946684800  == 2000-01-01T00:00:00+00:00 in ISO 8601
    t0 = 946684800

    count    = 0
    endcount = len(data)
    for a in data:
        newtime = _convertUnixtimeToDateTime(t0 + count)
        aa = a[0:11] + newtime + a[11+19:]
        if count < 30 or count > (endcount - 30): print("aa: ", aa) # a has no LF
        if count == 30: print(".......")
        writeFileA(csvfilename, aa)
        count += 1

    setNormalCursor()


def DB_convertCSVtoDB(DB_Connection, CSV_FilePath):
    """Read a *.log or *.his file and save into database
    It uses the variable 'pointer' created by getCSV to select and order columns
    """

    fncname = "DB_convertCSVtoDB: "

    dprint(fncname + "CSV_FilePath: ", CSV_FilePath)
    setDebugIndent(1)

    hilimit    = 30   # highest number of lines to print
    deltalimit = 30   # lines before hilimit to print
    lolimit    = hilimit - deltalimit

#   readlines fails when non-UTF-8 characters in file like after file data corruption
#   compare with geigerlog f'on getCSV()
#    with open(CSV_FilePath, "r") as cfghandle: # read CSV file as list of str
#        rlines = cfghandle.readlines()
    with open(CSV_FilePath, "rb") as cfghandle: # read CSV file as bytes
        byteline = cfghandle.read()
        #print("byteline:", byteline)

    strlines = ""
    for a in byteline.split(b"\n"):
        try:                    rl = a.decode("UTF-8")
        except Exception as e:  rl = "#" + str(a)
        strlines += rl + "\n"

    rlines = strlines.split("\n")

#TESTING limiting count of lines
    #linex = 8730                # breaks with 8670, i.e. line 8669
    #rlines = rlines[:linex]
    #for i in range(linex - 30, linex ):
    #    print("rlines[{}] : ".format( i), rlines[i], end="")
################################

    # reading lines like:(not shown: all have \n at the end!)   !!!!! not true: LF is gone at this stage
    # rlines[0]: #HEADER, File created from History Download Binary Data
    # rlines[1]: #ORIGIN, Downloaded <Date Unknown> from device '<Device Unknown>'
    # rlines[2]: #    0, 2018-12-19 10:18:26, Date&Time Stamp; Type:'history saving off', Interval:0 sec
    # rlines[3]: #   12, 2018-12-19 10:18:26, Tube Selected is:1  [0=both, 1=tube1, 2=tube2]
    # rlines[6]:     40, 2018-12-19 10:20:19,      ,      ,      0,       0
    # rlines[7]:     41, 2018-12-19 10:20:20,      ,      ,      0,       0
    # also possible:
    # rlines[2]: #FORMAT: '<#>ByteIndex, Date&Time, CPM, CPS' (Line beginning with '#' is comment)

    #print("rlines: len:{}, lines as read: ".format(len(rlines)), rlines[:50])

    sslines = []
    for i in range(0, len(rlines)):
        #print("rlines[{}]: len:{}, line as read: ".format(i, len(rlines[i])), rlines[i])
        #print("ord:", ord(rlines[i][0]))

        if rlines[i].strip() == "": continue

        if i >= lolimit and i <= hilimit:        wprint("wprint rlines[{}]: {}".format(i, rlines[i]))

        splitrlines = (rlines[i]).split(',')
        ssline=[]       # split and stripped rline
        for a in splitrlines:
            b = a.strip()
#???            if b == "": b = None
            ssline.append(b)
        sslines.append(ssline)
    #print("sslines: len:{}, lines: ".format(len(sslines)), sslines[:50])

    sqlData     = sqlInsertData
    sqlComments = sqlInsertComments

    for i in range(0, len(sslines)):

        #if i >= lolimit and i <= hilimit:      print("sslines[{}]: {}".format(i, sslines[i]))

        # in case there is no index, sslines[i][0][0] cannot be called
        try:
            ssli00 = sslines[i][0][0]
        except:
            ssli00 = ""

        #~if sslines[i][0][0] == '#':
        if ssli00 == '#':
            ss  = sslines[i][0][1:].strip()
            sss = ss.upper()
            if "HEADER" in sss:
                ctype = "1HEADER"
                if "HISTORY" in (", ".join(sslines[i])).upper():
                    ctype = "HEADER"
                    cjday = None                        # there is no date in His files!
                    cinfo = ", ".join(sslines[i][1:])
                elif "LOGFILE" in (", ".join(sslines[i])).upper():
                    ctype = "HEADER"
                    cjday = sslines[i][1]
                    cinfo = ", ".join(sslines[i][2:])
                else:
                    ctype = "HEADER"
                    cjday = sslines[i][1]
                    cinfo = ", ".join(sslines[i][1:])
            elif "ORIGIN:" in sss:              # with ':'
                ctype = "ORIGIN"
                cjday = None
                cinfo = sss[8:]
            elif "ORIGIN" in sss:
                ctype = "ORIGIN"                        # with ',' (implicit)
                cjday = None
                cinfo = ", ".join(sslines[i][1:])
            elif "FORMAT:" in sss:                      # with ':'
                continue
                ctype = "FORMAT"
                cjday = None
                cinfo = sss[8:] + ", " + ", ".join(sslines[i][1:])
            elif "FORMAT" in sss:                       # with ',' (implicit)
                continue

            elif "INDEX" in sss:
                continue
            else:
                cjday = None
                #print("sslines[i]:", i, sslines[i])
                lenssi = len(sslines[i])
                if lenssi > 1:
                    ctype = ss
                #    cjday = sslines[i][1]  # was gibt das an?
                    sx = []
                    for j in range(1, lenssi):
                        if sslines[i][j] != None:# if an item is None it cannot be joined
                            sx.append(sslines[i][j])
                        else:
                            sx.append(" ")
                    try:
                        cinfo = ", ".join(sx)
                    except:
                        cinfo = "something wrong in this line..." # needs to improve for error
                        vprint(i, ",  Comments: ", [ctype, cjday, "0 hours", cinfo])

                    if i <=3 and ctype == "LOGGING": cjday = None
                else:
                    ctype = ss
                    cjday = None
                    cinfo = ""

            if i >= lolimit and i <= hilimit:      wprint(i, ",  Comments: ", [ctype, cjday, "0 hours", cinfo])
            gglobs.currentConn.execute(sqlComments,  [ctype, cjday, "0 hours", cinfo])

        else:
            # Index, DateTime, CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  Temp, Press, Humid, RMCPM
            datalist = [None] * (gglobs.datacolsDefault + 1) # 12 x None
            # not all csv files have 12 items, i.e. sslines may not have 12 items
            # therefore fill up datalist from the bottom
            for j in range(0, (gglobs.datacolsDefault + 1)):
                try:
                    pointer_value = gglobs.pointer[j]
                    if pointer_value == -1:
                        val = None
                    else:
                        val = sslines[i][pointer_value]
                except:
                    val = None
                datalist[j] = val

            if i >= lolimit and i <= hilimit:      wprint(i, ",  data:     {}".format(datalist))

            if datalist[1] == None:
                ctype = datalist[0]
                cjday = None
                cinfo = "Missing DateTime - Record invalid:" + rlines[i][:-1]
                DB_Connection.execute(sqlComments,  [ctype, cjday, "0 hours", cinfo])
            else:
                DB_Connection.execute(sqlData,       datalist[0:2] +["0 hours"] + datalist[2:])

        try:
            #print("DB_convertCSVtoDB: datalist: ", datalist)
            pass
        except:
            pass

    DB_commit(DB_Connection)
    setDebugIndent(0)


def getCSV(CSV_FilePath):
    """get a csv file with option to reorder columns. The result is stored in
    variable 'pointer', which is used by DB_convertCSVtoDB to vonvert CSV to
    database file"""

    colCountCSV = gglobs.datacolsDefault + 1            # +1 = + index

    # this fails with non-UTF-8 characters in file, like when corrupted
    # with open(CSV_FilePath, "r", encoding='utf8') as cfghandle: # read CSV file as long str
    #    rlines = cfghandle.read()
    #    #print("rlines:", rlines)
    with open(CSV_FilePath, "rb") as cfghandle: # read CSV file as bytes
        byteline = cfghandle.read()
        #print("byteline:", byteline)

    rlines = ""
    for a in byteline.split(b"\n"):
        try:                    rl = a.decode("UTF-8")
        except Exception as e:  rl = "#" + str(a)
        rlines += rl + "\n"

    yourfile = QLabel("Your CSV file: {}".format(CSV_FilePath))
    yourfile.setFont(QFont("Sans",14,weight=QFont.Bold))

    csv_text = QPlainTextEdit()
    csv_text.setLineWrapMode(QPlainTextEdit.NoWrap)
    csv_text.setReadOnly(True)
    csv_text.appendPlainText(rlines)
    csv_text.moveCursor(QTextCursor.Start)

    demo = \
"""
#  Index,            DateTime,      CPM,      CPS,   CPM1st,   CPS1st,   CPM2nd,   CPS2nd,   CPM3rd,   CPS3rd,     Temp,    Press,    Humid,        X
   0, 2019-01-11 19:32:14,      181,        6,      168,        5,       13,        1,       77,        3,         ,         ,         ,
   1, 2019-01-11 19:32:18,      197,        3,      172,        2,       25,        1,       64,        4,     22.3,  1014.64,     45.7,       17
-----------------------------------------------------------------------------------------------------------------------------------------------------
Column0,             Column1,  Column2,  Column3,  Column4,  Column5,  Column6,  Column7,  Column8,  Column9, Column10, Column11, Column12, Column13"""

    demofile = QLabel("Default Association of Column Number and Data (Example Data)")
    demofile.setFont(QFont("Sans",14,weight=QFont.Bold))

    demo_text = QPlainTextEdit()
    demo_text.setLineWrapMode(QPlainTextEdit.NoWrap)
    demo_text.setReadOnly(True)
    demo_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    demo_text.setVerticalScrollBarPolicy  (Qt.ScrollBarAlwaysOff)
    demo_text.setMaximumHeight(120)
    demo_text.appendPlainText(demo)
    demo_text.moveCursor(QTextCursor.Start)

    # maxCols defines how many columns the CSV file is allowed to have
    maxCols         =  22              # all cols(=14) + None + 4 spare
    selectorList    = [""]* maxCols
    selectorList[0] = "None"           #  the None column: ignore the CSV data column
    for i in range(1, maxCols):
        selectorList[i] = "CSV Column "+str(i - 1)
    #print("selectorList:", selectorList) # =['None', 'Column 0', 'Column 1', 'Column 2', ...]

    # only as many col_selectors as there are columns finally; presently = 0...13 = 14
    col_selectors = [""]* colCountCSV
    for i in range(colCountCSV):
        col_selectors[i] = QComboBox()
        col_selectors[i].setMaxVisibleItems(25)
        col_selectors[i].addItems(selectorList)

        ### pick either one
        #col_selectors[i].setCurrentIndex(i + 1)    # every entry has same var as its index = all is preset
        col_selectors[i].setCurrentIndex(0)       # every entry is None                   = all is empty
        ###


    col_selectors[1].model().item(0) .setEnabled(False)


    # layout grid
    dataOptions=QGridLayout()
    dataOptions.setColumnStretch(1,10)          # the drop-down box cols
    dataOptions.setColumnStretch(3,10)          # the drop-down box cols
    dataOptions.setContentsMargins(5,5,5,5)     # spacing around the grid
    dataOptions.setVerticalSpacing(0)           # inner spacing

    #                                                          row, col
    dataOptions.addWidget(QLabel("Index:"),                     0,   0)
    dataOptions.addWidget(col_selectors[0],                     0,   1)
    dataOptions.addWidget(QLabel("DateTime:"),                  1,   0)
    dataOptions.addWidget(col_selectors[1],                     1,   1)

    for i, vname in enumerate(gglobs.varsBook):
        dataOptions.addWidget(QLabel(gglobs.varsBook[vname][0] + ":"),  i+2, 0)
        dataOptions.addWidget(col_selectors[i+2],                      i+2, 1)
        #dataOptions.addWidget(col_selectors[0],                      i+2, 1)
        if i >=5: break

    for i, vname in enumerate(gglobs.varsBook):
        if i <= 5: continue
        dataOptions.addWidget(QLabel(gglobs.varsBook[vname][0] + ":"),  i-6, 2)
        dataOptions.addWidget(col_selectors[i+2],                      i-6, 3)

    L0 = QLabel("Guidance:")
    L0.setFont((QFont("Sans",14,weight=QFont.Bold)))

    L5text = \
"""
- CSV file columns MUST be separated by comma
- A DateTime column MUST exist
- The DateTime column format MUST be "YYYY-MM-DD hh:mm:ss"\n  like: "2020-03-27 01:23:45"
- It is the order of the columns, which matters
- Set columns to 'None' to ignore
- Columns may be used multiple times
- Non-existing columns become 'Missing Values'
"""
    L5 = QLabel(L5text)
    L5.setFont((QFont("Sans",10,weight=QFont.Bold)))

    dial = QDialog()
    dial.setWindowIcon(gglobs.iconGeigerLog)
    dial.setFont(gglobs.fontstd)
    dial.setWindowTitle("Get Data from CSV File" )
    #dial.setWindowModality(Qt.ApplicationModal)
    #dial.setWindowModality(Qt.NonModal)
    dial.setWindowModality(Qt.WindowModal)
    dial.setMinimumWidth(1300)
    dial.setMinimumHeight(750)

    bbox    = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
    bbox.accepted.connect(lambda: dial.done(0))
    bbox.rejected.connect(lambda: dial.done(-1))

    layoutV2 = QVBoxLayout()
    layoutV2.addWidget(L0)
    layoutV2.addWidget(L5)
    layoutV2.addStretch()

    layoutH1 = QHBoxLayout()
    layoutH1.addLayout(layoutV2)
    layoutH1.addLayout(dataOptions)

    layoutV = QVBoxLayout(dial)            # uses dial as parent!
    layoutV.addWidget(yourfile)
    layoutV.addWidget(csv_text)
    layoutV.addWidget(demofile)
    layoutV.addWidget(demo_text)
    layoutV.addLayout(layoutH1)
    layoutV.addWidget(bbox)

    dexec = dial.exec_()

    if dexec == 0:
        gglobs.pointer = []
        for i in range(0, colCountCSV):
            gglobs.pointer.append(col_selectors[i].currentIndex() - 1) # -1 !
        return True
    else:
        gglobs.pointer = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] # ????
        return False

