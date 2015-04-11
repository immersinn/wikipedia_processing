"""
> Change this to work on any box
don't hard-code data paths

> Get this up and running so that a subset of the wiki collection
can be dumped to a mongo db

> add in ability to create a new db to hold the data (duh);
"RE-PRODUCABLE CODE"
"""

import sys
sys.path.append('/Users/immersinn/Dropbox/PythonCode/wikiprep/')
sys.path.append('/Users/immersinn/Dropbox/PythonCode/DBInterfaceStuff/dbconns/')
import wikixmlparse_example
import connectMon
wikimdb = connectMon.MongoConn()
wikimdb.makeDBConn('WikiData')
wikimdb.makeCollConn('articleDump')
fn = wikixmlparse_example.findFirstPage()
wikixmlparse_example.parseWikiXML(fn, wikimdb)
