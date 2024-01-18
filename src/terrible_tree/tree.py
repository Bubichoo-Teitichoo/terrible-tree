"""API."""
from __future__ import annotations

import platform
from fnmatch import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING

import natsort

from .icons import TREE_DIR_ICON, TREE_FILE_ICON

if TYPE_CHECKING:
    import os
    from collections.abc import Callable, Generator


class TreeItem(Path):
    """Extension to pathlib's Path object."""

    _flavour = Path()._flavour  # type: ignore[attr-defined]  # noqa: SLF001

    @property
    def icon(self) -> str:
        """Get the icon for the file type."""
        return TREE_DIR_ICON if self.is_dir() else TREE_FILE_ICON

    @staticmethod
    def hidden_filter(allow_hidden: bool) -> Callable[[Path], bool]:
        """
        Returns a function that can be passed to `filter` for filtering hidden files and directories.

        Args:
            allow_hidden (bool):
                If set to `True`, the returned function always returns True.
                If set to `False`, the returned fuction will return `False` if
                a `Path` to a hidden file or directory is given.

        Returns:
            Callable[[Path], bool]:
                Function that can be passed to a `filter`.
        """

        def closure(path: Path) -> bool:
            return not path.name.startswith(".") or allow_hidden

        return closure

    def iterdir_sorted(self) -> Generator[TreeItem, None, None]:
        """
        Yield path objects of the directory contents.

        The children are yielded in OS file explorer order.
        Special entries '.' and '..' are not included.

        Note:
            This function yields all directories yielded by `iterdir()`
            without further interation with the object. `Path` objects
            pointing to a file are buffered in a list and are yielded
            when the actual `iterdir()` function exits.

        Yields:
            Generator[TreeItem, None, None]:
                All items below the directory.
        """
        files: list[TreeItem] = []

        iterator = super(TreeItem, self.resolve()).iterdir() if self.is_windows_symlink() else super().iterdir()
        try:
            for item in natsort.os_sorted(iterator):
                resolved_item = item if not self.is_windows_symlink() else self.joinpath(item.name)

                if resolved_item.is_dir():
                    yield resolved_item
                else:
                    files.append(resolved_item)
        except PermissionError:
            pass
        yield from files

    def iterdir(self, *, include_hidden: bool = False) -> Generator[TreeItem, None, None]:
        """
        Yield path objects of the directory contents.

        The children are yielded in OS file explorer order.
        Special entries '.' and '..' are not included.

        Args:
            include_hidden (bool, optional):
                Whether or not hidden files and directories shall be included
                in the yielded items. Defaults to False.

        Yields:
            Generator[TreeItem, None, None]:
                All items below the directory. Items are sorted using natsort.os_sorted()
                and directories are yielded first then files.
                See `iterdir_sorted()`.
        """
        yield from filter(self.hidden_filter(include_hidden), self.iterdir_sorted())

    def is_windows_symlink(self) -> bool:
        """Workaround for Windows/NTFS weird symlinks that are not detected by the regular function."""
        if platform.system() == "Windows":
            return not self.absolute().is_relative_to(self.resolve())
        return False

    def as_string(self, *, absolute: bool = False) -> str:
        """
        Get the file name or absolute path as string including the associated icon.

        Args:
            absolute (bool, optional):
                Whether the abosulte path shall be returned or only the name of the file. Defaults to False.

        Returns:
            str: The name or absolute path of the path object.
        """
        line = [self.icon, self.name if not absolute else str(self.resolve().as_posix())]
        if self.is_windows_symlink():
            line.extend(["->", self.resolve().as_posix()])
        return " ".join(line)


class TerribleTree:
    """
    Implementation of a file tree.

    The class is an iterator that yields all files and directories under
    the given root.
    The files are yielded in OS file explorer order, which means that
    directories are yielded first then files.

    Directories are traversed recursively, hence the class keeps a
    context of files and directories that are yet to be yielded.
    """

    class EndOfTreeError(StopIteration):
        """Error raised if the end of a tree has been reached and `next` is called."""

    def __init__(
            self, root: os.PathLike | None = None, *, depth: int = 0, glob_filter: str | None = None, include_hidden: bool = False
    ) -> None:
        """
        Initialize a new instance.

        Args:
            root (os.PathLike | None): root of the tree.
            glob_filter (str | None): unix wildcard/glob style filter.
            include_hidden (bool):
                Whether or not to inlcude hidden files and directories.
        """
        self._context: list[TreeItem]
        self._depth : int
        self._hidden: bool

        self._root: TreeItem = TreeItem(root).resolve() if root else TreeItem.cwd()
        self._filter: str = glob_filter or "*"
        self.reset(depth, include_hidden=include_hidden)

    def __iter__(self) -> Generator[TreeItem, None, None]:
        """Iterates all files and directories under `root`."""
        while self._context:
            yield next(self)

    @property
    def root(self) -> TreeItem:
        """Get root of the tree."""
        return self._root

    def reset(self, depth: int = 0, *, include_hidden: bool = False) -> None:
        """Reset the tree to it's initial state."""
        self._depth = depth
        self._hidden = include_hidden
        self._context = self._build_subcontext(self.root)

    def __next__(self) -> TreeItem:
        """
        Get the next item from the Tree and remove it from the context.

        Raises:
            TerribleTree.EndOfTreeError:
                if the context is empty, which means that the end of the tree was reached.

        Returns:
            TreeItem: The next item in the tree.
        """
        if not self._context:
            raise TerribleTree.EndOfTreeError

        item = self._context.pop(0)
        if item.is_dir() and (not self._depth or self._depth > self.rel_depth(item)):
            leafs = self._build_subcontext(item)
            self._context[0:0] = leafs
        return item

    def peek(self, *, depth: int | None = None, default: TreeItem | None = None) -> TreeItem | None:
        """
        Get the next item or a specific item.

        Note:
            The item won't be removed from the context.

        Args:
            depth (int | None, optional):
                If not given the function will just return the next item from the context.
                If given the next item with the given depth is searched in the context and returned.
                Defaults to None.
            default (TreeItem | None, optional):
                Value that will be returned if the end of the tree was reached.
                If None an exception is raised. Defaults to None.

        Returns:
            TreeItem:
                Next item in the tree. If depth given the next item
                that matches the given depth.
            None: If depth was given an no matching item was found.

        """
        if not self._context:
            return default

        if depth is None:
            return self._context[0]
        for item in self._context:
            if self.rel_depth(item) == depth:
                return item
        return None

    def rel_depth(self, path: Path) -> int:
        """
        Get the depth of the given path relative to the tree root.

        Args:
            path (Path):
                path object that is relative to the tree root.

        Returns:
            int: depth relative to the root of the tree.
        """
        return len(path.relative_to(self.root).parts)

    def build(self) -> list[TreeItem]:
        """
        Build a full list of the file tree.

        Returns:
            list[TreeItem]:
                List containing the complete file tree.
        """
        return list(self)

    def _build_subcontext(self, item: TreeItem) -> list[TreeItem]:
        def fnmatch_closure(item: TreeItem) -> bool:
            if self._filter == "*":
                return True
            if item.is_dir():
                return bool(list(item.resolve().rglob(self._filter)))

            return fnmatch(item.as_posix(), self._filter)

        return list(filter(fnmatch_closure, item.iterdir(include_hidden=self._hidden)))
