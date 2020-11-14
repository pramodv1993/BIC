import numpy as np
import pandas as pd

# df = pd.read_csv("nodes.csv", sep="\t", index_col=None)

# graph = {
#     '1': {'2': 4, '3': 2, '4': 5},
#     '2': {'1': 4, '5': 2},
#     '3': {'1': 2, '6': 3, '7': 3},
#     '4': {'1': 5, '8': 2},
#     '5': {'2': 2, '6': 2, '9': 3},
#     '6': {'3': 3, '5': 2, '7': 3, '10': 4},
#     '7': {'3': 3, '6': 3, '8': 3},
#     '8': {'4': 2, '7': 3, '11': 3},
#     '9': {'5': 3, '10': 4},
#     '10': {'6': 4, '9': 4, '11': 5},
#     '11': {'8': 3, '10': 5}
# }




def dijkstra(fromNode, toNode, df):

    df1 = df.groupby("From")["To"].apply(list).reset_index()
    df1["distance"] = df.groupby("From")["distance"].apply(list).reset_index()["distance"]
    df1.columns = ["from", "to", "distance"]
    graph = {}
    for ind, row in df1.iterrows():
        graph[str(row["from"])] = {}
        for src, dist in list(zip(row["to"], row["distance"])):
            graph[str(row["from"])][str(src)] = dist

    shortest_distance = {}
    predecessor = {}
    unseenNodes = graph
    infinity = np.inf
    path = []
    for node in unseenNodes:
        shortest_distance[node] = infinity
    shortest_distance[fromNode] = 0

    while unseenNodes:
        minNode = None
        for node in unseenNodes:
            if minNode is None:
                minNode = node
            elif shortest_distance[node] < shortest_distance[minNode]:
                minNode = node

        for childNode, weight in graph[minNode].items():
            if weight + shortest_distance[minNode] < shortest_distance[childNode]:
                shortest_distance[childNode] = weight + shortest_distance[minNode]
                predecessor[childNode] = minNode
        unseenNodes.pop(minNode)

    currentNode = toNode
    while currentNode != fromNode:
        try:
            path.insert(0, currentNode)
            currentNode = predecessor[currentNode]
        except KeyError:
            print('Path not reachable')
            break
    path.insert(0, fromNode)
    if shortest_distance[toNode] != infinity:
        print('Shortest distance is ' + str(shortest_distance[toNode]))
        print('Shortest path -> ' + str(path))
    return path
