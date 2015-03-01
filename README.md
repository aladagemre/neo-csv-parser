REQUIREMENTS
==============

python package: neo4jrestclient

You can install it by:
    pip install neo4jrestclient

FORMATTING
================================

Each row consists of ONE node and/or ONE relationship:
    - Only node properties
    - Only relationships
    - ONE node and its ONE relationship.

Fields are of the form:

Node.<NODELABEL>.<PROPERTYNAME>             : defines property value of the source node.
Rel.<RELLABEL>.<TARGETLABEL>                : defines unique name of the target node.
Rel.<RELLABEL>.<TARGETLABEL>.<RELPROPERTY>  : defines property value of the target node.


Sample cases:
Case 1
Tom Smith => WorkedAt => NexTech

- Node.Person.UniqueName [Tom Smith]
- Node.Person.EmailWork [tom@smith.com]
- Node.Person.FirstName [Tom]
- Node.Person.LastName [Smith]
- Rel.WorkedAt.Company [NexTech]
- Rel.WorkedAt.Company.JobTitle [Partner]

Case 2
Tom Smith => Likes => John Brown
- Node.Person.UniqueName [Tom Smith]
- Rel.Likes.Person  [John Brown]
- Rel.Likes.Person.Rating [5]


Warning: If you want to provide multiple [but same] relationships for the same person, put them in seperate rows.

Ex:
Jack Brown WorkedAt IBM
Jack Brown WorkedAt Microsoft

will create two WorkedAt relationships.


SAMPLE INPUT DATA
========================
data1-nodes.csv: Contains only the nodes and their properties.
data1-relations.csv: Contains only the relationships (with FROM/TO unique names and relationship properties)

data2.csv: Contains ONE node with its properties and ONE relationship per row.
data3.csv: Contains ONE node with its properties and MULTIPLE relationships spanning over 3 rows. Pay attention that
you redundantly wrote properties and only thing changing is relationship data for Tom Smith.
So you may prefer data1 format above (nodes-edges seperated)

CONFIG.INI FILE
==========================
Here you can set the CSV delimiter (; or ,) and quote character (").


CHECKING DUPLICATES (check_duplicates.py)
=========================================
Checks for duplicate UniqueNames in the input file. It's worth looking at it.
If you are sure that UniqueName properties are unique or you're just giving multiple relationships from the same person,
there's no need for running this script.

Example Usage:
python check_duplicates.py data2.csv
python check_duplicates.py bigdata.csv


IMPORTING NEW PEOPLE (NewPeople.py)
==============================
You should give the csv file as parameter to the script. Sample usages:

python NewPeople.py data1-nodes.csv
python NewPeople.py data1-relations.csv
python NewPeople.py bigdata.csv

If you want to skip duplicate records, just give --skip parameter. Duplicate rows (except for the first one) will be written in duplicates.csv.
python NewPeople.py bigdata.csv --skip

* Non-unicode characters will be deleted while reading.
* Logging will tell you what's been processed at the moment.


CHECKING UNICODE CHARACTERS (check_unicode.py)
===============================
You may want to check whether a csv file contains non-unicode characters. Although these characters will be deleted
by the NewPeople script (to be compatible with Neo4j), avoiding these characters in the csv file will make the
processing more consistent.

John;Brown .á.
will be cleaned as:
John;Brown ..

If in the future you correct it as
John;Brown

in the csv file and run the NewPeople script, John Brown will be a new person, different from John Brown ..


DELETE RELATIONSHIPS (delete_relationships.py)
======================
CAUTION: Deletes all the relationships in the database.
Just in case you want to test the script.

DELETE NODES (delete_nodes.py)
======================
CAUTION: Deletes all the nodes in the database (if there exists no relationships binded to them).
Just in case you want to test the script.


SEARCH (Search.py)
=====================
python Search.py

and follow instructions.
1) Enter the node type: Person
2) Enter the query: FirstName=John,LastName=Brown
3) Enter outputfile: search_results.csv

And look at search_results.csv.