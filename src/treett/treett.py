from __future__ import annotations

import fnmatch
import argparse

from typing import List
from typing import Tuple

from .item import TreeItem
from .icons import TREE_FORK
from .icons import TREE_BRANCH
from .icons import TREE_TERMINAL

def extract_parents_from_treelist(lst: List[Tuple[TreeItem, int]], start, end, base_depth):
    result = []
    
    # if start is 0 set it to none otherwise the root item is droped
    if 0 == start:
        start = None

    # every directory with a lower depth is a direct parent
    # after copying a parent the base_depth is reset
    for item, depth in lst[end:start:-1]:
        if depth < base_depth and item.is_dir():
            result.append((item, depth))
            base_depth = depth
    return reversed(result)


def main():
    argument_parser = argparse.ArgumentParser("Modern Tree")
    argument_parser.add_argument('path', nargs='?', type=TreeItem, default=TreeItem('.'))
    argument_parser.add_argument('--hidden', action='store_true', help='Include "hidden folders"')
    argument_parser.add_argument('--dirs', action='store_true', help='Show directories only')
    argument_parser.add_argument('--depth', type=int, default=-1, help='Set max. display depth')
    argument_parser.add_argument('-f', '--filter', type=str, default='*', help='Filter files (glob syntax)')


    arguments = argument_parser.parse_args()

    root: TreeItem = arguments.path
    filtered_list = treelist = root.create_list(
        arguments.depth,
        arguments.dirs,
        arguments.hidden
    )

    #if arguments.dirs:
    #    filtered_list = [(item, depth) for item, depth in treelist if item.is_dir()]
    #    treelist = filtered_list
                
    if arguments.filter != '*':        
        filtered_list = []
        copy_idx = 0
        forward_copy = 0
        for idx, (item, depth) in enumerate(treelist):
            if 0 != forward_copy and depth > forward_copy:
                filtered_list.append((item, depth))
                copy_idx = idx
                continue
            else:
                forward_copy = 0

            # apply the given filter
            # copy all direct parents of a matching item into the result
            if fnmatch.fnmatch(str(item.path).replace(r'\\', '/'), arguments.filter) or fnmatch.fnmatch(str(item.path.name), arguments.filter):
                #print(item)
                filtered_list.extend(extract_parents_from_treelist(treelist, copy_idx, idx, depth))
                filtered_list.append((item, depth))
                #if not item.is_dir():
                copy_idx = idx
                #else:
                #    forward_copy = depth

    if not filtered_list:
        print(root.name_with_icon(True))
        exit()

    max_depth = max(filtered_list, key=lambda x: x[1])[1] + 1
    depth_matrix = max_depth * [False]
    for idx, (item, depth) in enumerate(filtered_list):
        
        # set everything from the current depth to max as enabled
        for didx in range(depth, max_depth):
            depth_matrix[didx] = True

        # check wheather the current item is the last on this depth until
        # depth drops again
        # set the current element as flagged
        depth_matrix[depth] = False
        for _, d in filtered_list[idx+1:]:
            if d == depth:
                depth_matrix[depth] = True
            if depth > d:
                break

        indentation = []
        # we dont want to indent the root directory
        if 0 != depth:
            # if the current item has at least 2 parents and the parent is
            # not flagged draw a connecting branch.
            # otherwise just draw some whitespaces
            for pidx in range(1, item.has_relative_directories(root)):
                if depth_matrix[pidx]:
                    indentation.append(TREE_BRANCH + 2 * " ")
                else:
                    indentation.append(3 * " ")

            # if the current item is flagged draw a terminal instead of a fork
            if not depth_matrix[depth]: #or (idx + 1) == len(filtered_list) or filtered_list[idx+1][1] < depth:
                indentation.append(TREE_TERMINAL)
            else:
                indentation.append(TREE_FORK)

        print(f'{"".join(indentation)}{item.name_with_icon(depth == 0)}')

if __name__ == '__main__':
    main()
