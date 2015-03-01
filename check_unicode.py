import sys
def parse(filename):
    print "Problematic rows:"
    print "="*30
    reader = open(filename)
    for row in reader:
        try:
            unicode(row)
        except:
            print row.strip()


if __name__ == "__main__":
    parse(sys.argv[1])