from room import Room
from player import Player
from world import World

import multiprocessing
import os
import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
# map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []

def get_directions(path):
    """return list of directions for given path"""
    directions = []

    for i in range(len(path) - 1):
        room = world.rooms[path[i]]
        next_room = world.rooms[path[i + 1]]

        for direction in room.get_exits():
            if next_room == room.get_room_in_direction(direction):
                directions.append(direction)

    return directions

def get_path_always_right():
    """return path for always going right, backtrack at dead ends or already visited"""
    pass

def get_shortest_path():
    """return shortest path to visit all rooms"""
    
    def path_finder(queue):
        try:
            visited, path, room = queue.get(True, 1)
        except multiprocessing.TimeoutError:
            return

        visited = visited.copy().add(room.id)
        path = path.copy().append(room.id)

        dead_end = True
        for direction in 'nesw':
            next_room = room.get_room_in_direction(direction)
            if next_room:
                if not next_room.id in visited:
                    queue.put((visited, path, next_room))
                    dead_end = False
        
        if dead_end:
            get_shortest_unvisited_path()

    queue = multiprocessing.Queue()
    jobs = []
    for i in range(1, os.cpu_count):
        p = multiprocessing.Process(target=path_finder, args=(queue,))
        jobs.append(p)

    for p in jobs:
        p.join()

def get_shortest_unvisited_path(visited, path, room):
    """return shortest path to a room adjacent to unvisited rooms"""
    pass

# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
