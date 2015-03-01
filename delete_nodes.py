from neo4jrestclient.query import Q
from neo4jrestclient.client import GraphDatabase

gdb = GraphDatabase("http://localhost:7474/db/data/")
cql = "MATCH (u) DELETE u"
try:
    gdb.query(cql)
except Exception, e:
    print "Please run delete_relationships.py before running this script."
    print e