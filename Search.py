import csv
from neo4jrestclient.query import Q
from neo4jrestclient.client import GraphDatabase

label = raw_input("Enter the node label (e.g. Person): ")
query = raw_input('Enter query (e.g. FirstName=John,EmailWork=jrpsu@me.com): ')

def property_match(name, value):
    """
    Returns the Query for given property name.
    Ex: Q("FirstName", exact="John")
    """
    return Q(name, exact=value)


gdb = GraphDatabase("http://localhost:7474/db/data/")

queries=query.split(",")
qlist = []
for q in queries:
    Q_obj = property_match(*q.split("="))
    qlist.append(Q_obj)


def get_relation_fields(results):
    fields = set()
    for node in results:
        # continue on to write data
        dict_ = get_node_fields(node)

        for rel in node.relationships.all():
            target_label = list(rel.end.labels)[0]._label
            rel_props = rel.properties
            target_title = "Rel.%(rel_type)s.%(target_label)s" % {'rel_type': rel.type, 'label': label, 'target_label': target_label}
            target_unique_name = rel.end.properties.get('UniqueName')
            dict_[target_title] = target_unique_name
            for key, value in rel_props.iteritems():
                # Person.WorksAt.Company.Name
                title = "Rel.%(rel_type)s.%(target_label)s.%(key)s" % {'rel_type': rel.type, 'label': label, 'target_label': target_label, 'key': key}
                dict_[title] = value
        dw.writerow(dict_)

def get_node_fields(node):
    """
    Normally node.properties contain: UniqueName, FirstName, ... etc.
    We want to write Node.Person.UniqueName, Node.Person.FirstName, ... etc.
    This function does that conversion.
    """
    d = {}
    for key, value in node.properties.iteritems():
        newkey = "Node.%s.%s" % (list(node.labels)[0]._label, key)
        d[newkey] = value
    return d

print qlist
result = gdb.nodes.filter(reduce(lambda x,y: x & y, qlist))
results = [res for res in result]
print "Number of results: %d" % len(results)
if results:
    for result in results:
        print result.properties.get('UniqueName')
    print
    outfile = raw_input("Enter output file:")
    #outfile="search_results.csv"
    if outfile:
        keyset = reduce(lambda x,y: x+y, [node.properties.keys() for node in results])
        keyset = map(lambda x: "Node.%s.%s" % (list(node.labels)[0]._label, x), keyset)
        all_keys = set(keyset)#.union(get_relation_fields(results))

        with open(outfile,'w') as fou:
            dw = csv.DictWriter(fou, delimiter=';', fieldnames=all_keys)

            dw.writeheader()

            for node in results:
                # continue on to write data
                dict_ = get_node_fields(node)

                """for rel in node.relationships.all():
                    target_label = list(rel.end.labels)[0]._label
                    rel_props = rel.properties
                    target_title = "Rel.%(rel_type)s.%(target_label)s" % {'rel_type': rel.type, 'label': label, 'target_label': target_label}
                    target_unique_name = rel.end.properties.get('UniqueName')
                    dict_[target_title] = target_unique_name
                    for key, value in rel_props.iteritems():
                        # Person.WorksAt.Company.Name
                        title = "Rel.%(rel_type)s.%(target_label)s.%(key)s" % {'rel_type': rel.type, 'label': label, 'target_label': target_label, 'key': key}
                        dict_[title] = value"""
                dw.writerow(dict_)
    else:
        print "No output path given. Doing nothing."



"""cql = "MATCH (n:%(label)s)-[r]->(v) WHERE %(query)s RETURN n,r" % {'query': query, 'label': label}
for result in gdb.query(cql):
    print result[0]
    print result[0].get('data')
    print result[0].get('outgoing_relationships')"""