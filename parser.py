import logging
import csv
import string
import ConfigParser

FORMAT = '%(asctime)-15s [%(levelname) 8s] %(message)s'
logging.basicConfig(format=FORMAT, level="INFO")
logger = logging.getLogger('neoparser')

class Node:
    def __init__(self):
        self.properties = {}

    def __repr__(self):
        return self.properties.get('UniqueName', 'Node X')


class Relationship:
    def __init__(self):
        self.properties = {}

    def __repr__(self):
        if self.label:
            try:
                return "%s [%s: %s]" % (self.label, self.target_label, self.target_value)
            except:
                return self.label
        return "Relationship X"


def find_uniquename_col(fields):
    """
    Finds the column index with UniqueName property.
    """
    for i, field in enumerate(fields):
        cols = field.split(".")
        if len(cols) == 3 and cols[2] == "UniqueName":
            return i

def parse(filename, skip_duplicates=False):
    config = ConfigParser.ConfigParser()
    config.readfp(open('config.ini'))
    delimiter = config.get('CSV', 'delimiter', ';')
    quotechar = config.get('CSV', 'quotechar', '"')
    nodes = []
    logger.info("Reading csv file: %s", filename)
    with open(filename, "rU") as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        i = 0
        duplicates = []
        names_sofar = set()
        for row in reader:
            if i == 0:
                fields = map(lambda x: x.strip(), row)
                unique_name_index = find_uniquename_col(fields)
                if unique_name_index is None:
                    return None
            else:
                # clear non-unicode chars.
                row = map(lambda cell: filter(lambda x: x in string.printable, cell.strip()).strip(), row)
                unique_name = row[unique_name_index]
                if unique_name in names_sofar:
                    duplicates.append(row)
                    logger.warning("Duplicate row: %s", ";".join(row))
                    if skip_duplicates:
                        continue
                else:
                    names_sofar.add(row[unique_name_index])

                node = Node()
                relationship = Relationship()
                for j, value in enumerate(row):
                    try:
                        cols = fields[j].split(".")
                    except IndexError,e:
                        print "Following row has more columns than the fields:"
                        print row
                        print fields
                        return -1

                    if cols[0] == "Node":
                        # its a node
                        # Node.Person.UniqueName
                        # Node.Person.LastName
                        # Node.Project.UniqueName
                        node.label = cols[1]
                        node.properties[cols[2]] = value

                    elif cols[0] == "Rel":
                        # its a relationship
                        # Rel.WorkedAt.Company
                        # Rel.Likes.Person
                        # Rel.WorkedAt.Company.UntilDate

                        relationship.label = cols[1] # WorkedAt
                        relationship.target_label = cols[2] # Company
                        if len(cols) == 3:
                            # Rel.WorkedAt.Company
                            relationship.target_value = value
                        elif len(cols) == 4:
                            # Rel.WorkedAt.Company.UntilDate
                            # if relationship property is given
                            relationship.properties[cols[3]] = value # 20.01.2014

                node.relationship = relationship
                nodes.append(node)
            i += 1
        logger.info("Parsing finished: %d nodes", len(nodes))
        logger.info("Fields: %s" % ", ".join(fields))
        handle_duplicates(duplicates)

        return nodes


def handle_duplicates(duplicates):
    o = open("duplicates.csv", "w")
    for dup in duplicates:
        o.write(";".join(dup) + "\n")
    o.close()
