from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import py2neo


class Graph:
    """
    Neo4j queries often only use 1 CPU core.
    This simple wrapper can make it handle a
    defined maximum of concurrent queries.
    It's not very nice, but it could speed things up.
    """

    def __init__(self, *a, concurrent_queries: int = 1, **k):
        self.executor = ThreadPoolExecutor(max_workers=concurrent_queries)
        self.graph = py2neo.Graph(*a, **k)
        self.graphs = Queue()
        for _ in range(concurrent_queries):
            self.graphs.put(py2neo.Graph(*a, **k))
        self.__dict__.update(
            {parent_attribute: getattr(self.graph, parent_attribute)
             for parent_attribute in dir(self.graph)
             if not parent_attribute.startswith('_')
             and parent_attribute not in ['data', 'run', 'evaluate']}
        )

    def data(self, *a, as_future: bool = False, **k):
        """
        Does the same things as py2neo.Graph.data, but can return Futures
        instead of results. Call .result() in the calling code to get
        the actual output.
        """
        if not as_future:
            return self.graph.data(*a, **k)

        def graph_data(*a, **k):
            graph = self.graphs.get(block=True)
            data = graph.data(*a, **k)
            self.graphs.put(graph)
            return data

        return self.executor.submit(graph_data, *a, **k)

    def run(self, *a, as_future: bool = False, **k):
        """
        Does the same things as py2neo.Graph.run, but can return Futures
        instead of results. Call .result() in the calling code to get
        the actual output.
        """
        if not as_future:
            return self.graph.run(*a, **k)

        def graph_run(*a, **k):
            graph = self.graphs.get(block=True)
            data = graph.run(*a, **k)
            self.graphs.put(graph)
            return data

        return self.executor.submit(graph_run, *a, **k)

    def evaluate(self, *a, as_future: bool = False, **k):
        """
        Does the same things as py2neo.Graph.evaluate, but can return Futures
        instead of results. Call .result() in the calling code to get
        the actual output.
        """
        if not as_future:
            return self.graph.evaluate(*a, **k)

        def graph_evaluate(*a, **k):
            graph = self.graphs.get(block=True)
            data = graph.evaluate(*a, **k)
            self.graphs.put(graph)
            return data
        
        return self.executor.submit(graph_evaluate, *a, **k)
