from queue import Queue
import pickle

# MAP:
# 0 ----- 1
#   \    / \
#    2 --   3 ----- 4
#     \   /
#  5 --- 6      7
#   \    |     /
#    8   9 - 10 - 11
#    |   |          \
#   12 - 13          -14


class Map:
    """
    Mostly for testing
    """

    def __init__(self):

        self.locations = [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
        ]

        self.connections = [
            (1, 2),
            (2, 3),
            (0, 1, 6),
            (1, 4, 6),
            (3,),
            (6, 8),
            (2, 3, 5, 9),
            (10,),
            (5, 12),
            (6, 10, 13),
            (7, 9, 11),
            (10, 14),
            (8, 13),
            (12, 9),
            (11,),
        ]

    def getConnections(self, location_id):
        return self.connections[location_id]


class StarMap:
    """
    Routing information on the EVE star map
    """

    def __init__(self):

        file = open("connections_data", "r+b")
        connections_data = pickle.load(file)
        file.close()

        self.sys_connections = connections_data

    def getConnections(self, location_id):

        for system in self.sys_connections:
            if system[1] == location_id:
                return system[2]

        return None

    def getName(self, location_id):

        for system in self.sys_connections:
            if system[1] == location_id:
                return system[0]

        return None


class Route:
    def __init__(self):

        self.map = StarMap()

        self.frontier = Queue()

        self.breadcrum = dict()

        self.current_pos = None

    def findRoute(self, start, end):
        # print("routing...")

        self.frontier.put(start)
        self.breadcrum[start] = None

        while not self.frontier.empty():
            current_pos = self.frontier.get()

            for next_pos in self.map.getConnections(current_pos):
                if next_pos not in self.breadcrum:
                    self.frontier.put(next_pos)
                    self.breadcrum[next_pos] = current_pos

            if current_pos == end:
                break

        path = []
        crum = current_pos

        while crum != start:
            path.append(crum)
            crum = self.breadcrum[crum]

        path.append(start)
        path.reverse()

        # print("routing complete!")
        # print(path)
        return path
