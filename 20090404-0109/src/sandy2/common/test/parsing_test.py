#! /usr/bin/python

import unittest

import sandy2.common.parsing

class ParserTest(unittest.TestCase):

    parser = None

    def setUp(self):
        mp = DummyMicroParser("dummy", previous=['non-existant'])
        self.parser = sandy2.common.parsing.Parser(micro_parsers=[mp], actions=[])

    def tearDown(self):
        # nop
        return

    def testSingleMicroParser(self):
        metadata = self.parser.parse_message("No real content")
        print "Metadata: ", metadata
        self.assertNotEqual(None, metadata['dummy_key'], 'Dummy key was not set')

    def testTopSort(self):
        micro_parsers = [    DummyMicroParser("first (real)", next=["second (fake)"]),
                            DummyMicroParser("third (real)", previous=["second (fake)"]),
                            DummyMicroParser("fifth (real)", previous=["fourth (real)"]),
                            DummyMicroParser("fourth (real)", previous=["third (real)"], next=["sixth (fake)"]),
                            DummyMicroParser("end", previous=["sixth (fake)", "fifth (real)"])
        ]

        ordered = sandy2.common.ordering.topological_sort(micro_parsers)
        print "Top sort", map(lambda node : node.id,  ordered)
        for node in ordered:
            self.assertTrue(node.id.find("fake") == -1, "Found a fake node")

        micro_parsers = [   DummyMicroParser('10', previous=['9']),
                            DummyMicroParser('8', next=['9'], previous=['7']),
                            DummyMicroParser('4', next=['6', '7']),
                            DummyMicroParser('2', next=['4'], previous=['0']),
                            # this is an implementation detail that this will be scheduled first
                            DummyMicroParser('0')
        ]
        ordered = sandy2.common.ordering.topological_sort(micro_parsers)

        print map(lambda p: p.id, ordered)

        index = -1
        for parser in ordered:
            self.assertTrue(int(parser.id) > index, "Wrongly ordered node")
            index = int(parser.id)




class DummyMicroParser(sandy2.common.parsing.IMicroParser):

    def __init__(self, id, previous=[], next=[]):
        self.is_preceeded_by = previous
        self.id = id
        self.is_followed_by = next

    def micro_parse(self, metadata):
        metadata["dummy_key"] = "dummy_value"

if __name__ == '__main__':
    unittest.main()


