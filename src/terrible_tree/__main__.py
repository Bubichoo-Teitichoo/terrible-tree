"""main module defining CLI commands."""
from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TypeVar

import click

from terrible_tree.icons import (
    TREE_BRANCH,
    TREE_FORK,
    TREE_TERMINAL,
)

from .tree import TerribleTree, TreeItem

T = TypeVar("T", bound=Callable)


def common_option(func: T) -> T:
    """Decorator to add common options to all commands."""
    click.help_option("-h", "--help")(func)
    click.version_option(None, "-v", "--version")(func)
    return func


@click.group()
@common_option
def main() -> None:
    """A terrible reimplementation of the tree utility."""


@main.command(name="tree")
@common_option
@click.argument("path", type=TreeItem, default=TreeItem.cwd())
@click.option("-f", "--filter", "glob_filter", type=str, default="*", help="Unix shell-style wildcard filter.")
@click.option("-a", "--all", "include_hidden", is_flag=True, type=bool, default=False, help="Print hidden files.")
def print_tree(path: TreeItem, glob_filter: str, include_hidden: bool) -> None:
    """
    List the content of a directory recursively.

    If [PATH] is omitted the current working directory will be used.

    To filter the result one can use the `-f`/`--filter` option, which uses
    unix style wildcard to filter the output.

    To include hidden files and directories in the tree, one simply has to set
    the `-a`/`--all` flag.
    """
    tree = TerribleTree(path, glob_filter=glob_filter, include_hidden=include_hidden)
    click.echo(path.as_string(absolute=True))
    for item in tree:
        depth = tree.rel_depth(item)
        # add indentations and branch continuations to the line.
        # if the tree contains an item with a depth in the range of [1:`depth`] we add a branch i.e. pipe(|)
        # if not we just add 3 white spaces, indenting the line.
        line = [f"{TREE_BRANCH if tree.peek(depth=idx) else ' '}{2 * ' '}" for idx in range(1, depth)]

        # if the tree contains  more items on the with the same depth we add a fork
        # if not we add a teminal.
        line.append(f"{TREE_FORK if tree.peek(depth=depth) else TREE_TERMINAL}{item.as_string()}")
        click.echo("".join(line))


@main.command(name="ls")
@common_option
@click.argument("path", type=TreeItem, default=TreeItem())
@click.option("-a", "--all", "include_hidden", is_flag=True, type=bool, default=False)
def print_list(path: TreeItem, include_hidden: bool) -> None:
    """Print the content of a directory."""
    for leaf in path.iterdir(include_hidden=include_hidden):
        click.echo(leaf.as_string())


if __name__ == "__main__":
    sys.exit(main())
