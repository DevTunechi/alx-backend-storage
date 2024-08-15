#!/usr/bin/env python3


"""
This module contains a single function that updates all the topics of a
school document based on the name
"""


def update_topics(mongo_collection, name, topics):
    """
    This updates all the topics in a school based on the name
    """
    mongo_collection.update_many({"name": name}, {"$set": {"topics": topics}})
