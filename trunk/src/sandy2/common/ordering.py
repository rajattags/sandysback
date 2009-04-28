__author__="james"
__date__ ="$05-Jan-2009 22:14:29$"

debug = True

class INode(object):
    """A common type to allow ordering of parsers and actions.
    """

    """The id of this node"""
    id = 'unknown'

    """The ids of parsers that need to have been run before this one"""
    is_preceeded_by = set()

    """The ids of parsers that need to be run after this one"""
    is_followed_by = set()

class CyclicDependencyError(Exception):
    """An error for graph algorithms"""


class DependencyList:
    """List capable of accepting INodes and other objects.
    """
    def __init__(self, nodes=None, configure=None):
        """Take an initial list of nodes, and a callable method. The callable is applied to each of the nodes on addition to the list.
        """
        self._nodes = nodes if nodes else list()
        self._is_ordered = False
        if configure is not None and callable(configure):
            self.configure = configure
            for node in nodes:
                configure(node)
        else:
            self.configure = self.__nop
        
    def __iter__(self):
        if not self._is_ordered:
            new_nodes = topological_sort(self._nodes)
            self._nodes = new_nodes
            self._is_ordered = True
        return self._nodes.__iter__()    
    
    def __nop(self, obj):
        pass
      
    def append(self, obj):
        """Append an object to the list.
        """
        self._is_ordered = False
        self.configure(obj)
        self._nodes.append(obj)
    
    def extend(self, obj):
        """Append an object to the list.
        """
        self.append(obj)
        
    def __str__(self):
        return str(self._nodes)

def topological_sort(list_of_nodes):
    
    if debug:
    	print to_dot(list_of_nodes)
    
    id_to_nodes, inbound_nodes, outbound_nodes = _create_adjacency_matrix(list_of_nodes)
    schedule = _create_new_node_list(id_to_nodes, inbound_nodes, outbound_nodes)
    return schedule

def _create_new_node_list(id_to_nodes, inbound_nodes, outbound_nodes):
    schedule = []
    ready_for_scheduling = []
    num_nodes = len(id_to_nodes)
    while len(schedule) != num_nodes:
    # find the next node to schedule
        next_node_id = None
        if len(ready_for_scheduling) > 0:
            next_node_id = ready_for_scheduling.pop()
        # this loop is only run once, on first run
        else:
            for id, incomers in inbound_nodes.items():
                if len(incomers) == 0:
                    del inbound_nodes[id]
                    if next_node_id is None:
                        next_node_id = id
                    else:
                        ready_for_scheduling.append(id)
        if (next_node_id is None):
            # we probably have a cycle, panic
            raise CyclicDependencyError()
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
            incoming = inbound_nodes.get(next, set())
            incoming.discard(id)
            if len(incoming) == 0:
                del inbound_nodes[next]
                ready_for_scheduling.append(next)
    return schedule


    
def _create_adjacency_matrix(list_of_nodes):
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
        
    
    return id_to_nodes, inbound_nodes, outbound_nodes


def to_dot(list_of_nodes):
    id_to_nodes, inbound_nodes, outbound_nodes = _create_adjacency_matrix(list_of_nodes)
    
    all_strings = ["digraph G {"]
    
    
    # render all the nodes first.
    strings = ["%s" % (id) for id in id_to_nodes.keys()]
    
    all_strings.append("\tnode [shape=box]; %s" % (" ".join(strings)))
    
    rendered = set()
    
    for node, inbound in inbound_nodes.items():
        for link in inbound:
            if (not link in rendered) and (not id_to_nodes.has_key(link)):
                rendered.add(link)
                all_strings.append("\tnode [shape=ellipse]; %s" % (link))
                
            all_strings.append("\t%s -> %s [weight = 10 color = gray];" % (link, node))
            
    
    
    
    schedule = _create_new_node_list(id_to_nodes, inbound_nodes, outbound_nodes)
    
    prev = None
    for node in schedule:
        if prev:
            all_strings.append("\t%s -> %s [penwidth = 5 weight = 100];" % (prev.id, node.id))
        prev = node
    
    
    all_strings.append("}")
    return "\n".join(all_strings)
    
    
