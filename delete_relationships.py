from neo4jrestclient.query import Q
from neo4jrestclient.client import GraphDatabase

gdb = GraphDatabase("http://localhost:7474/db/data/")
cql = "MATCH (u)-[r]->(v) DELETE r"
gdb.query(cql)