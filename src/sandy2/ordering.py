

__author__="james"
__date__ ="$05-Jan-2009 22:14:29$"


def topological_sort(list_of_nodes):

    outbound_nodes = dict()
    inbound_nodes = dict()
    id_to_nodes = dict()

    # set up an adjacency map, based on nodes which can be processed after this one.
    # we have to do this here, rather than rely on the data given to us by the nodes,
    # because we have to unite the incoming and outbounds of each node.
    for node in list_of_nodes:
        id = getattr(node, 'id', 'unknown')
        if id is 'unknown':
            id = node.__class__.__name__
            setattr(node, 'id', id)

        id_to_nodes[id] = node

        followers = outbound_nodes.setdefault(id, set())
        for my_follower in getattr(node, 'is_followed_by', []):
            followers.add(my_follower)
            inbound_nodes.setdefault(my_follower, set()).add(id)
            outbound_nodes.setdefault(my_follower, set())

        incomers = inbound_nodes.setdefault(id, set())
        for my_preceeder in getattr(node, 'is_preceeded_by', []):
            incomers.add(my_preceeder)
            outbound_nodes.setdefault(my_preceeder, set()).add(id)
            inbound_nodes.setdefault(my_preceeder, set())

    schedule = []
    ready_for_scheduling = []
    while len(schedule) != len(list_of_nodes):

        # find the next node to schedule
        next_node_id = None
        if len(ready_for_scheduling) > 0:
            next_node_id = ready_for_scheduling.pop()
        else:
            # this loop is only run once, on first run
            for id, incomers in inbound_nodes.items():
                if len(incomers) == 0:
                    del inbound_nodes[id]
                    if next_node_id is None:
                        next_node_id = id
                    else:
                        ready_for_scheduling.append(id)
                       
        if (next_node_id is None):
            # we probably have a cycle, panic
            raise GraphError()

        # we probably have node, so we can do something with it
        next_node = id_to_nodes.get(next_node_id, None)
        if (next_node is not None):
            # like schedule it, if it's not a placeholder
            schedule.append(next_node)

        # now, we want to delete this node from incoming lists
        outbound = outbound_nodes[next_node_id]
        del outbound_nodes[next_node_id]

        id = next_node_id
        for next in outbound:
            incoming = inbound_nodes.get(next,set())
            incoming.discard(id)
            if len(incoming) == 0:
                del inbound_nodes[next]
                ready_for_scheduling.append(next)

    return schedule




class INode(object):
    """A common type to allow ordering of parsers and actions.
    """

    """The id of this node"""
    id = 'unknown'

    """The ids of parsers that need to have been run before this one"""
    is_preceeded_by = set()

    """The ids of parsers that need to be run after this one"""
    is_followed_by = set()

class GraphError(Exception):
    """An error for graph algorithms"""
