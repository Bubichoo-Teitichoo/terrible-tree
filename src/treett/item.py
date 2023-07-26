from __future__ import annotations

from pathlib import Path

from typing import List
from typing import Tuple
from typing import Union
from typing import Generator

from .icons import TREE_DIR_ICON
from .icons import TREE_FILE_ICON

class TreeItem:
    def __init__(self, path: Union[str,Path]):
        self.path: Path = Path(path).resolve()

    def __iter__(self) -> Generator[TreeItem, None, None]:
        if not self.is_dir():
            return
        dirs = []
        files = []
        for item in self.path.iterdir():
            item = TreeItem(item)
            if item.is_dir():
                dirs.append(item)
            else:
                files.append(item)
        yield from dirs + files

    def __str__(self) -> str:
        return self.name_with_icon()

    def __repr__(self) -> str:
        return f'<TreeItem - {self.path}>'
    
    @property
    def name(self) -> str:
        return self.path.name

    def is_dir(self) -> bool:
        return self.path.is_dir()        

    def has_relative_directories(self, root: TreeItem) -> int:
        root: Path = root.path
        return len(self.path.relative_to(root).parents)

    def has_leafs(self) -> bool:
        return self.path.is_dir() and bool(list(self.path.iterdir()))

    def name_with_icon(self, resolve: bool = False) -> str:
        return f'{TREE_DIR_ICON if self.path.is_dir() else TREE_FILE_ICON} {str(self.path) if resolve else self.path.name}'

    def create_list(self, max_depth: int = -1, dirs: bool = False, hidden: bool = False) -> List[Tuple[TreeItem, int]]:
        def treelist_recursive_create(item: TreeItem, depth: int = 0) -> List[Tuple[TreeItem, int]]:
            if not hidden and item.name.startswith('.'):
                return []
            if dirs and item.path.is_file():
                return []

            result = []
            result.append((item, depth))
            if -1 == max_depth or depth < max_depth:
                for subitem in item:
                    result.extend(treelist_recursive_create(subitem, depth+1))
            return result
        return treelist_recursive_create(self)