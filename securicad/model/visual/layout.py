from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import ceil, sqrt
from typing import Any, Generator, Optional, TypedDict, Union

from securicad.model.model import Model
from securicad.model.object import Object
from securicad.model.visual.container import Container
from securicad.model.visual.exceptions import (
    DuplicateLayoutObjectException,
    EmptyLayoutException,
)
from securicad.model.visual.view import View

OBJECT_RADIUS = 45
GROUP_PADDING = 35

ITEM_PADDING = 1.5 * OBJECT_RADIUS
TREE_SPACING = 150

ItemType = Union["Layout", Object]


def item_size(item: ItemType) -> tuple[float, float]:
    if isinstance(item, Layout):
        return item._width, item._height
    else:
        assert isinstance(item, Object)
        diameter = OBJECT_RADIUS * 2
        return diameter, diameter


@dataclass
class Position:
    x: float
    y: float


class OffsetMap(TypedDict, total=False):
    x_offset: float
    y_offset: float


class Layout(ABC):
    def __init__(
        self,
        name: str,
        icon: Optional[str] = None,
        expand: Optional[bool] = None,
        tags: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        offset: Optional[dict[ItemType, OffsetMap]] = None,
        item_padding: float = ITEM_PADDING,
    ) -> None:
        self.name = name
        self.icon = icon
        self.expand = expand
        self.tags = tags
        self.description = description
        self.color = color
        self.offset: dict[ItemType, OffsetMap] = {} if offset is None else dict(offset)
        self.item_padding = item_padding
        self._parent: Optional[Layout] = None
        self._items: list[ItemType] = []
        self._positions: dict[ItemType, Position] = {}
        self._width: float = OBJECT_RADIUS * 2 if expand is False else 0
        self._height: float = OBJECT_RADIUS * 2 if expand is False else 0

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"

    def add_item(self, item: ItemType) -> None:
        if isinstance(item, Layout):
            for obj in item.objects():
                if self.has_object(obj):
                    raise DuplicateLayoutObjectException(self, obj)
            item._parent = self
        else:
            assert isinstance(item, Object)
            if self.has_object(item):
                raise DuplicateLayoutObjectException(self, item)
        self._items.append(item)

    def objects(self) -> Generator[Object, None, None]:
        for item in self._items:
            if isinstance(item, Layout):
                yield from item.objects()
            else:
                assert isinstance(item, Object)
                yield item

    def has_object(self, obj: Object) -> bool:
        for item in self._items:
            if isinstance(item, Layout):
                if item.has_object(obj):
                    return True
            else:
                assert isinstance(item, Object)
                if item.id == obj.id:
                    return True
        return False

    def build(self, model: Model) -> View:
        if self.icon is not None:
            raise ValueError("Views cannot have icons")
        if self._parent is not None:
            raise ValueError("Only top-level layouts can be built into views")
        self._layout()
        view = model.create_view(self.name)
        self._build_items(view)
        return view

    def _build_items(self, container: Container) -> None:
        for item, position in self._positions.items():
            if isinstance(item, Layout):
                if item.icon is None:
                    raise ValueError("Groups must have icons")
                group = container.create_group(
                    item.name, item.icon, position.x, position.y
                )
                if item.expand is not None:
                    group.meta["expand"] = item.expand
                if item.tags is not None:
                    group.meta["tags"] = item.tags
                if item.description is not None:
                    group.meta["description"] = item.description
                if item.color is not None:
                    group.meta["color"] = item.color
                item._build_items(group)
            else:
                assert isinstance(item, Object)
                container.add_object(item, position.x, position.y)

    @abstractmethod
    def _layout(self) -> None:
        if not self._items:
            raise EmptyLayoutException(self)
        for item in self._items:
            if isinstance(item, Layout):
                item._layout()

    def _update_width(self, content_width: float) -> None:
        if self.expand is False:
            return
        layout_width = content_width + 2 * GROUP_PADDING
        if layout_width > self._width:
            self._width = layout_width

    def _update_height(self, content_height: float) -> None:
        if self.expand is False:
            return
        layout_height = content_height + 2 * GROUP_PADDING
        if layout_height > self._height:
            self._height = layout_height

    def _position_item(self, item: ItemType, x: float, y: float) -> None:
        if isinstance(item, Layout) and item.expand is not False:
            x += GROUP_PADDING
            y += GROUP_PADDING
        x_offset = self.offset.get(item, {}).get("x_offset", 0)
        y_offset = self.offset.get(item, {}).get("y_offset", 0)
        self._positions[item] = Position(x + x_offset, y + y_offset)


class HorizontalLayout(Layout):
    def __init__(
        self,
        name: str,
        icon: Optional[str] = None,
        expand: Optional[bool] = None,
        tags: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        offset: Optional[dict[ItemType, OffsetMap]] = None,
        item_padding: float = ITEM_PADDING,
        align_middle: bool = True,
    ) -> None:
        super().__init__(
            name, icon, expand, tags, description, color, offset, item_padding
        )
        self.align_middle = align_middle

    def _layout(self) -> None:
        super()._layout()
        content_height: float = 0
        for item in self._items:
            _, item_height = item_size(item)
            if item_height > content_height:
                content_height = item_height
        x: float = 0
        for item in self._items:
            item_width, item_height = item_size(item)
            y = (content_height - item_height) / 2 if self.align_middle else 0
            self._position_item(item, x=x, y=y)
            self._update_width(x + item_width)
            x += item_width + self.item_padding
        self._update_height(content_height)


class VerticalLayout(Layout):
    def __init__(
        self,
        name: str,
        icon: Optional[str] = None,
        expand: Optional[bool] = None,
        tags: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        offset: Optional[dict[ItemType, OffsetMap]] = None,
        item_padding: float = ITEM_PADDING,
        align_center: bool = True,
    ) -> None:
        super().__init__(
            name, icon, expand, tags, description, color, offset, item_padding
        )
        self.align_center = align_center

    def _layout(self) -> None:
        super()._layout()
        content_width: float = 0
        for item in self._items:
            item_width, _ = item_size(item)
            if item_width > content_width:
                content_width = item_width
        y: float = 0
        for item in self._items:
            item_width, item_height = item_size(item)
            x = (content_width - item_width) / 2 if self.align_center else 0
            self._position_item(item, x=x, y=y)
            self._update_height(y + item_height)
            y += item_height + self.item_padding
        self._update_width(content_width)


class GridLayout(Layout):
    def __init__(
        self,
        name: str,
        icon: Optional[str] = None,
        expand: Optional[bool] = None,
        tags: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        offset: Optional[dict[ItemType, OffsetMap]] = None,
        item_padding: float = ITEM_PADDING,
        columns: Optional[int] = None,
        align_center: bool = True,
        align_middle: bool = True,
    ) -> None:
        super().__init__(
            name, icon, expand, tags, description, color, offset, item_padding
        )
        if columns is not None and columns < 1:
            raise ValueError("'columns' must at least be 1")
        self.columns = columns
        self.align_center = align_center
        self.align_middle = align_middle

    def _layout(self) -> None:
        super()._layout()
        cols = ceil(sqrt(len(self._items))) if self.columns is None else self.columns
        rows = ceil(len(self._items) / cols)
        item_matrix = self._item_matrix(rows, cols)
        row_height, col_width = self._grid_size(item_matrix, rows, cols)
        y: float = 0
        for row in range(rows):
            x: float = 0
            for col in range(cols):
                item = item_matrix[row][col]
                if item is None:
                    break
                item_width, item_height = item_size(item)
                x_offset = (col_width[col] - item_width) / 2 if self.align_center else 0
                y_offset = (
                    (row_height[row] - item_height) / 2 if self.align_middle else 0
                )
                self._position_item(item, x=x + x_offset, y=y + y_offset)
                self._update_width(x + col_width[col])
                x += col_width[col] + self.item_padding
            self._update_height(y + row_height[row])
            y += row_height[row] + self.item_padding

    def _item_matrix(self, rows: int, cols: int) -> list[list[Optional[ItemType]]]:
        item_matrix: list[list[Optional[ItemType]]] = []
        index = 0
        for _ in range(rows):
            row: list[Optional[ItemType]] = []
            for _ in range(cols):
                if index < len(self._items):
                    row.append(self._items[index])
                    index += 1
                else:
                    row.append(None)
            item_matrix.append(row)
        return item_matrix

    def _grid_size(
        self, item_matrix: list[list[Optional[ItemType]]], rows: int, cols: int
    ) -> tuple[list[float], list[float]]:
        row_height: list[float] = [0] * rows
        col_width: list[float] = [0] * cols
        for row in range(rows):
            for col in range(cols):
                item = item_matrix[row][col]
                if item is None:
                    break
                item_width, item_height = item_size(item)
                if item_width > col_width[col]:
                    col_width[col] = item_width
                if item_height > row_height[row]:
                    row_height[row] = item_height
        return row_height, col_width


class TreeLayout(Layout):
    def __init__(
        self,
        name: str,
        icon: Optional[str] = None,
        expand: Optional[bool] = None,
        tags: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        offset: Optional[dict[ItemType, OffsetMap]] = None,
        item_padding: float = ITEM_PADDING,
        tree_spacing: float = TREE_SPACING,
        stem: Optional[list[ItemType]] = None,
        align_middle: bool = True,
    ) -> None:
        super().__init__(
            name, icon, expand, tags, description, color, offset, item_padding
        )
        self.tree_spacing = tree_spacing
        self.stem: set[ItemType] = set() if stem is None else set(stem)
        self.align_middle = align_middle

    def _layout(self) -> None:
        super()._layout()

        stem: list[ItemType] = []
        stem_width: float = 0
        stem_height: float = 0
        crown: list[ItemType] = []
        crown_width: float = 0
        crown_height: float = 0
        for item in self._items:
            item_width, item_height = item_size(item)
            if item in self.stem:
                stem.append(item)
                if item_width > stem_width:
                    stem_width = item_width
                if stem_height == 0:
                    stem_height = item_height
                else:
                    stem_height += item_height + self.item_padding
            else:
                crown.append(item)
                if crown_width == 0:
                    crown_width = item_width
                else:
                    crown_width += item_width + self.item_padding
                if item_height > crown_height:
                    crown_height = item_height

        content_width = max(stem_width, crown_width)
        self._update_width(content_width)
        self._update_height(stem_height + self.tree_spacing + crown_height)

        y: float = 0
        for item in stem:
            item_width, item_height = item_size(item)
            self._position_item(item, x=(content_width - item_width) / 2, y=y)
            y += item_height + self.item_padding

        x: float = (content_width - crown_width) / 2
        for item in crown:
            item_width, item_height = item_size(item)
            y_offset = (crown_height - item_height) / 2 if self.align_middle else 0
            self._position_item(item, x=x, y=stem_height + self.tree_spacing + y_offset)
            x += item_width + self.item_padding
