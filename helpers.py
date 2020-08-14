import sys
import json
import re

from neo4jdriver import GetNeo4j
from datetime import datetime

def demo():
    temp = GetNeo4j()
    data = temp.get_data()

    convert_data(data)

def data_search(search, type, condition="", limit=0):
    temp = GetNeo4j()
    if type == 0:
        # Text search
        string_condition = parse_string_condition(condition)
        data = temp.get_data_specific(search, string_condition, limit)
    else:
        data = temp.get_cypher_search(search)
    return convert_data(data)


def parse_string_condition(condition):
    result = ""
    list_item = condition.split('&')
    for item in list_item:
        if item.find("=on") > -1:
            type_node = re.match(r'.*?condition-(.*?)=.*$', item).group(1).capitalize()
            result += " or node:"+type_node if len(result) > 0 else "where node:"+type_node

    return result

def data_detail(id, limit):
    # print(str, type)
    temp = GetNeo4j()
    data = temp.get_data_detail(id, limit)
    # print(data)
    return convert_data(data, id)

def convert_data(data, id=0):
    nodes = []
    relationships = []
    for item in data:
        # print(item)
        # sys.exit()
        if len(item) == 3:
            nodes.append(convert_node(item[0], id))
            nodes.append(convert_node(item[2], id))
            relationships.append(convert_relationship(item[1]))
        else:
            nodes.append(convert_node(item[0], id))

    result = {
    "results": [{
        "columns": ["user", "entity"],
        "data": [{
            "graph": {
                "nodes": nodes,
                "relationships": relationships
            }
        }]
    }],
    "errors": []
    }
    # write_to_JSON_file('static/json', 'data', result)
    return json.dumps(result)


def convert_node(nodes_object, center_node):
    # print(dir(nodes_object))
    # print(nodes_object, len(nodes_object))
    return {
        "id": nodes_object.id,
        "labels": list(nodes_object.labels),
        "centerNode": center_node,
        "properties": convert_datetime(nodes_object._properties),
    }


def convert_relationship(relationship_object):
    # print(dir(relationship_object))
    # print(relationship_object, len(relationship_object))
    return {
        "id": relationship_object.id,
        "type": relationship_object.type,
        "startNode": relationship_object.nodes[0].id,
        "endNode": relationship_object.nodes[1].id,
        "properties": convert_datetime(relationship_object._properties)
    }


def convert_datetime(properties):
    # print(properties)
    if "updated_at" in properties:
        # print(type(properties), properties["updated_at"], type(properties["updated_at"].year))
        # print(properties["updated_at"].time())
        data = str(datetime(properties["updated_at"].year, properties["updated_at"].month,
                        properties["updated_at"].day, properties["updated_at"].hour, properties["updated_at"].minute))
        del properties["updated_at"]
        properties["update_at"] = data

    return properties

def write_to_JSON_file(path, fileName, data):
    filePathNameWExt = './' + path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp)

def more_data(node_id):
    temp = GetNeo4j()
    data = temp.get_more_infomations(node_id)
    return data

if __name__ == '__main__':
    demo()