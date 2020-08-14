#!/usr/bin/env python
import os, sys

from neo4j import GraphDatabase, basic_auth

class GetNeo4j:
    # driver = GraphDatabase.driver('bolt://127.0.0.1:7474', auth=basic_auth("neo4j", "datalake"))
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = os.getenv('PORT', '7474')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'datalake')

    def __init__(self):
        self.driver = GraphDatabase.driver('bolt://'+self.HOST, auth=basic_auth(self.NEO4J_USERNAME, self.NEO4J_PASSWORD), max_connecion_pool_size=9999999999, connection_acquisition_timeout=30)
        self.db = self.get_db()

    def close(self):
        self.driver.close()

    def get_db(self):
        return self.driver.session()

    def get_data(self):
        with self.driver.session() as session:
            return session.run("match (n)-[r]-(t) where rand()<0.1 return * limit 50").values()

    def get_data_specific(self, search, condition, limit):
        with self.driver.session() as session:
            return session.run("CALL db.index.fulltext.queryNodes('fulltextsearch', '"+search+"')"
                               " yield node "+condition+" return node limit "+limit).values()

    def get_data_detail(self, id, limit):
        with self.driver.session() as session:
            return session.run("match (n)-[r]-(t) where id(n)={id} return * limit {limit}", {'id': int(id), 'limit':limit}).values()

    def get_cypher_search(self, search):
        with self.driver.session() as session:
            return session.run(search).values()

    def get_more_infomations(self, node_id, limit=10):
        result = dict({'ajax_status': 0})
        with self.driver.session() as session:
            result['images'] = session.run("match (n)-[r:TAG_IMAGE]-(t) where id(n)={id} and t.full_size_url is not null return t.full_size_url limit {limit}", {'id': int(node_id), 'limit':limit}).values()
            if not result['images']:
                result['images'] = session.run(
                    "match (n)-[r]-(t:Album)--(i:Image) where id(n)={id} and i.full_size_url is not null return i.full_size_url limit {limit}",
                    {'id': int(node_id), 'limit': limit}).values()
            result['status'] = session.run("match (n)-[r:WRITE]-(s:Status) where id(n)={id} with s.like + s.wow + s.haha + s.bored + s.grrr + s.heart as reaction, s, n "
                                           " where reaction is not null return s.content, s.style, s.fb_id, reaction order by reaction desc limit {limit}", {'id': int(node_id), 'limit':limit}).values()
            result['influencers'] = session.run("match p=(n)-[:WRITE]->(s:Status)<-[r*0..1]-(t:Person) where id(n)={id} return distinct t.name, t.link, count(distinct(r)) as number order by number desc limit {limit}"
                                                , {'id': int(node_id), 'limit': limit}).values()
            result['ajax_status'] = 1
        return result