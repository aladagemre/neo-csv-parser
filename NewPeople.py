# encoding: utf-8
import random
import sys
import csv
import logging
from neo4jrestclient.query import Q
from neo4jrestclient.client import GraphDatabase
from parser import parse

FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT, level="INFO")
logger = logging.getLogger('neoeval')

gdb = GraphDatabase("http://localhost:7474/db/data/")


def get_or_create_label(label_name):
    """
    returns label with given label name
    input: Person
    output: people
    """
    try:
        label = gdb.labels.get(label_name)
    except KeyError:
        label = gdb.labels.create(label_name)
    return label

people = get_or_create_label("Person")
companies = get_or_create_label("Company")


def property_match(node, property_name):
    """
    Returns the Query for given property name.
    Ex: Q("FirstName", exact="John")
    """
    return Q(property_name, exact=node.properties.get(property_name))

def evaluate(node):
    """
    Evaluates the given node with its relationship.
    """
    neonode = update_node(node)
    update_relationship(node, neonode)

def update_node(node):
    """
    Creates or updates given node.
    """
    logger.info("Current: %s" % node)
    lookup = property_match(node, "UniqueName")
    neonodes = get_or_create_label(node.label)
    result = neonodes.filter(lookup)
    result = [item for item in result]

    if not result:
        # if no nodes exists yet, create the new node.
        neonode = gdb.nodes.create(**node.properties)
        neonodes.add(neonode)
        logger.info("Creating new node: %s" % node)
    else:
        # if nodes exists, update
        neonode = result[0]
        neonode.properties = node.properties
        logger.info("Updating existing node: %s" % node)

    return neonode

def update_relationship(node, neonode):
    """
    Creates or updates relationship of given node.
    """
    try:
        target_value = node.relationship.target_value
    except:
        target_value = None

    if target_value:
        # Create relationships
        # Get Company label
        target_objects = get_or_create_label(node.relationship.target_label)
        # Find the target company
        target = [item for item in target_objects.filter(Q('UniqueName', exact=node.relationship.target_value))]
        logger.debug("Target: %s", target)
        if not target:
            logger.debug("target doesnt exist: %s", node.relationship.target_value)
            # target node is not created yet, create it.
            property_dict = {'UniqueName': node.relationship.target_value}
            target = gdb.nodes.create(**property_dict)
            target_objects.add(target)
        else:
            # target node has already been created.
            target = target[0]

        rels = [item for item in neonode.relationships.outgoing(types=[node.relationship.label])]
        for rel in rels:
            if rel.end == target:
                # this is what we're looking for.
                with gdb.transaction(update=False):
                    prop = rel.properties
                    prop.update(**node.relationship.properties)
                    rel.properties = prop
                rel.update()
                break
        else:
            # if we couldn't find the target, create it.
            rel = neonode.relationships.create(node.relationship.label, target, **node.relationship.properties)
    else:
        logger.warning("Empty target node value for: %s", node)


def main(filename, skip_duplicates=False):
    if skip_duplicates:
        skip_duplicates = True
    nodes = parse(filename, skip_duplicates)
    if nodes == -1:
        logger.error("Parsing error. Quitting.")
    elif nodes:
        logger.info("Now evaluating all the nodes.")
        for node in nodes:
            evaluate(node)
        logger.info("Evaluation finished.")
    else:
        logger.error("Make sure you have Node.XXX.UniqueName field in the csv file.")

if __name__ == "__main__":
    num_args = len(sys.argv)
    if num_args < 2:
        logger.error("Insufficient arguments. Usage: python NewPeople.py input.csv [--skip]")
    elif num_args == 2:
        main(sys.argv[1])
    elif num_args == 3:
        main(sys.argv[1], sys.argv[2])
    elif num_args > 3:
        logger.error("You should give max 2 arguments: filename [--skip]")

