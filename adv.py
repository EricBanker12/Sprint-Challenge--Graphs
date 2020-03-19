from room import Room
from player import Player
from world import World

import multiprocessing
import os
import queue
import random
import time

from ast import literal_eval

def get_directions(world, path):
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
    # visited = set()
    # stack = [world.starting_room]
    # path = [world.starting_room]
    # direction = world.starting_room.get_exits()[0]
    
    # while len(visited) < len(world.rooms):
    pass

def get_path_within_limit(world, limit=960):
    """return shortest path to visit all rooms"""

    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    jobs = []

    q.put((world.starting_room, []))
    
    for i in range(1, os.cpu_count()):
        p = multiprocessing.Process(target=path_finder, args=(world, q, r, limit))
        jobs.append(p)
        p.start()

    path = r.get(True)

    for p in jobs:
        p.kill()

    return path

def get_shortest_path(world):
    """return shortest path to visit all rooms"""

    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    jobs = []

    q.put((world.starting_room, []))
    
    for i in range(os.cpu_count() // 2):
        p = multiprocessing.Process(target=path_finder, args=(world, q, r))
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()

    min_length = None
    min_path = None
    for i in range(r.qsize()):
        path = r.get()
        path_len = len(path)
        if min_length == None or path_len < min_length:
            min_length = path_len
            min_path = path
    
    return min_path

def path_finder(world, q, r, limit=960):
    while True:
        try:
            room, path = q.get(True, 0.5)
        except:
            break

        path = [*path, room.id]

        if len(path) > limit:
            break

        if len(set(path)) < len(world.rooms):
            dead_end = True
            for direction in room.get_exits():
                next_room = room.get_room_in_direction(direction)
                if next_room:
                    if not next_room.id in path:
                        q.put((next_room, path))
                        dead_end = False
            
            if dead_end:
                next_q = get_shortest_unvisited_path(room, path, limit)
                if next_q:
                    q.put(next_q)
                else:
                    break
        else:
            r.put(path)

def get_shortest_unvisited_path(room, path, limit=960):
    """return shortest path to a room adjacent to unvisited rooms"""
    visited = set(path)
    temp_visited = set()
    q = queue.Queue()
    q.put((room, path))

    while True:
        room, path = q.get()
        if len(path) > limit:
            return None
        if not room.id in temp_visited:
            temp_visited.add(room.id)
            for direction in room.get_exits():
                next_room = room.get_room_in_direction(direction)
                if not next_room.id in visited:
                    return (room, path)
                q.put((next_room, [*path, next_room.id]))

def main():
    # Load world
    world = World()

    # You may uncomment the smaller graphs for development and testing purposes.
    # map_file = "maps/test_line.txt"
    # map_file = "maps/test_cross.txt"
    # map_file = "maps/test_loop.txt"
    # map_file = "maps/test_loop_fork.txt"
    map_file = "maps/main_maze.txt"

    # Loads the map into a dictionary
    room_graph=literal_eval(open(map_file, "r").read())
    world.load_graph(room_graph)

    # Print an ASCII map
    world.print_rooms()

    player = Player(world.starting_room)

    # Fill this out with directions to walk
    # traversal_path = ['n', 'n']
    start_time = time.time()
    traversal_path = get_directions(world, get_path_within_limit(world, 960))
    print(f'traversal_path:\n{traversal_path}\n{len(traversal_path)} directions')
    print(f'{time.time() - start_time:.1}s')

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

if __name__ == "__main__":
    main()
