import ConfigParser
import logging
import csv
import string
import collections
import sys
from parser import find_uniquename_col

FORMAT = '%(asctime)-15s [%(levelname) 8s] %(message)s'
logging.basicConfig(format=FORMAT, level="INFO")
logger = logging.getLogger('duplicate_checker')

def parse(filename):
    config = ConfigParser.ConfigParser()
    config.readfp(open('config.ini'))
    delimiter = config.get('CSV', 'delimiter', ';')
    quotechar = config.get('CSV', 'quotechar', '"')
    nodes = []
    logger.info("Reading csv file: %s", filename)
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        i = 0
        d = collections.defaultdict(list)

        for row in reader:
            if i == 0:
                fields = map(lambda x: x.strip(), row)
                print fields
                unique_name_index = find_uniquename_col(fields)
                if unique_name_index is None:
                    print "No UniqueName field found"
                    return None
            else:
                # clear non-unicode chars.
                row = map(lambda cell: filter(lambda x: x in string.printable, cell.strip()).strip(), row)
                unique_name = row[unique_name_index]
                d[unique_name].append(row)
            i += 1
        print "="*30
        for unique_name, row_list in d.iteritems():
            if len(row_list) > 1:
                for row in row_list:
                    print row
                print "="*30

if __name__ == "__main__":
    parse(sys.argv[1])