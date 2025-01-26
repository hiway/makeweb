"""
Implement Graph DB for Journal
"""

import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import List, Set, Optional, Dict, Any, Union
from uuid import uuid4
from collections import deque
from graphviz import Digraph
from typing import List, Set, Dict, Any, Union, Optional, Tuple


class Journal:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.db = None

    async def connect(self):
        """Establish database connection."""
        self.db = await aiosqlite.connect(self.db_path)
        return self.db

    async def disconnect(self):
        """Close database connection."""
        if self.db:
            await self.db.close()
            self.db = None

    @staticmethod
    def generate_id() -> str:
        """Generate a unique ID for a block using UUID4."""
        return str(uuid4())

    async def initialize(self):
        """Create necessary tables if they don't exist."""
        if not self.db:
            await self.connect()

        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS blocks (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                source_id TEXT,
                target_id TEXT,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id),
                FOREIGN KEY (source_id) REFERENCES blocks(id),
                FOREIGN KEY (target_id) REFERENCES blocks(id)
            )
        """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                block_id TEXT,
                key TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (block_id, key),
                FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE
            )
        """
        )

        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS block_references (
                source_id TEXT,
                target_id TEXT,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id, context),
                FOREIGN KEY (source_id) REFERENCES blocks(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES blocks(id) ON DELETE CASCADE
            )
        """
        )

        await self.db.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS blocks_fts USING fts5(
                id UNINDEXED,
                content,
                type UNINDEXED
            )
        """
        )
        await self.db.commit()

    async def _extract_references(self, content: str) -> List[str]:
        """Extract reference IDs from content using [[reference]] syntax."""
        import re

        pattern = r"\[\[(.*?)\]\]"
        return re.findall(pattern, content)

    async def _update_references(self, block_id: str, content: str) -> None:
        """Update references for a block based on its content."""
        # First, remove old references
        async with self.db.execute(
            "DELETE FROM block_references WHERE source_id = ?", (block_id,)
        ):
            await self.db.commit()

        # Extract and create new references
        refs = await self._extract_references(content)
        for ref in refs:
            # Find target blocks that match the reference
            async with self.db.execute(
                "SELECT id FROM blocks WHERE content LIKE ?", (f"%{ref}%",)
            ) as cursor:
                targets = await cursor.fetchall()
                for target in targets:
                    await self.db.execute(
                        """
                        INSERT INTO block_references (source_id, target_id, context)
                        VALUES (?, ?, ?)
                        """,
                        (block_id, target[0], ref),
                    )
        await self.db.commit()

    async def create_block(
        self, content: str, block_type: str, block_id: Optional[str] = None
    ) -> str:
        """Create a new block with optional ID and process any references."""
        block_id = block_id or self.generate_id()
        try:
            await self.db.execute(
                "INSERT INTO blocks (id, content, type) VALUES (?, ?, ?)",
                (block_id, content, block_type),
            )
            await self.db.commit()

            # Process references in content
            await self._update_references(block_id, content)

            # Update FTS index
            await self.db.execute(
                "INSERT INTO blocks_fts(id, content, type) VALUES (?, ?, ?)",
                (block_id, content, block_type),
            )
            await self.db.commit()
            return block_id
        except aiosqlite.IntegrityError:
            if block_id:  # If provided ID conflicts, generate a new one
                return await self.create_block(content, block_type)
            raise

    async def edit_block(self, block_id: str, content: str) -> bool:
        """Update a block's content and update references and search index."""
        async with self.db.execute(
            """
            UPDATE blocks 
            SET content = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (content, block_id),
        ):
            # Update references
            await self._update_references(block_id, content)

            # Update FTS index
            await self.db.execute(
                "INSERT INTO blocks_fts(id, content, type) SELECT id, content, type FROM blocks WHERE id = ?",
                (block_id,),
            )
            await self.db.commit()
            return True

    async def change_block_type(self, block_id: str, new_type: str) -> bool:
        """Change a block's type."""
        async with self.db.execute(
            "UPDATE blocks SET type = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_type, block_id),
        ):
            await self.db.commit()
            return True

    async def set_metadata(self, block_id: str, key: str, value: str) -> bool:
        """Set metadata key-value pair for a block."""
        async with self.db.execute(
            """
            INSERT OR REPLACE INTO metadata (block_id, key, value)
            VALUES (?, ?, ?)
            """,
            (block_id, key, value),
        ):
            await self.db.commit()
            return True

    async def get_metadata(
        self, block_id: str, key: Optional[str] = None
    ) -> Dict[str, str]:
        """Get all metadata or specific key for a block."""
        if key:
            async with self.db.execute(
                "SELECT key, value FROM metadata WHERE block_id = ? AND key = ?",
                (block_id, key),
            ) as cursor:
                row = await cursor.fetchone()
                return {row[0]: row[1]} if row else {}
        else:
            async with self.db.execute(
                "SELECT key, value FROM metadata WHERE block_id = ?",
                (block_id,),
            ) as cursor:
                return {row[0]: row[1] async for row in cursor}

    async def search_blocks(self, query: str) -> List[Dict[str, Any]]:
        """Search blocks using full-text search."""
        blocks = []
        async with self.db.execute(
            """
            SELECT b.* FROM blocks b
            JOIN blocks_fts f ON b.id = f.id
            WHERE blocks_fts MATCH ?
            ORDER BY rank
            """,
            (query,),
        ) as cursor:
            async for row in cursor:
                blocks.append(
                    {
                        "id": row[0],
                        "content": row[1],
                        "type": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                    }
                )
        return blocks

    async def get_backlinks(self, block_id: str) -> List[Dict[str, Any]]:
        """Get all blocks that reference this block."""
        backlinks = []
        async with self.db.execute(
            """
            SELECT b.*, r.context FROM blocks b
            JOIN block_references r ON b.id = r.source_id
            WHERE r.target_id = ?
            """,
            (block_id,),
        ) as cursor:
            async for row in cursor:
                backlinks.append(
                    {
                        "id": row[0],
                        "content": row[1],
                        "type": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                        "context": row[5],
                    }
                )
        return backlinks

    async def would_create_cycle(
        self, start_id: str, end_id: str, visited=None
    ) -> bool:
        """Check if adding a link would create a cycle using DFS."""
        if visited is None:
            visited = set()

        if start_id == end_id:
            return True

        if start_id in visited:
            return False

        visited.add(start_id)

        async with self.db.execute(
            "SELECT target_id FROM links WHERE source_id = ?", (start_id,)
        ) as cursor:
            children = await cursor.fetchall()

        for child in children:
            if await self.would_create_cycle(child[0], end_id, visited):
                return True

        return False

    async def link_blocks(self, parent_id: str, child_id: str) -> bool:
        """Link two blocks if it doesn't create a cycle."""
        if await self.would_create_cycle(child_id, parent_id):
            return False

        await self.db.execute(
            "INSERT INTO links (source_id, target_id, type) VALUES (?, ?, ?)",
            (parent_id, child_id, "direct"),
        )
        await self.db.commit()
        return True

    async def get_block(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a block by its ID."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, content, type, created_at, updated_at FROM blocks WHERE id = ?",
                (block_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "content": row[1],
                        "type": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                    }
                return None

    async def get_children(self, block_id: str) -> List[Dict[str, Any]]:
        """Get all blocks that are linked from this block."""
        children = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT b.* FROM blocks b
                JOIN links l ON b.id = l.target_id
                WHERE l.source_id = ?
            """,
                (block_id,),
            ) as cursor:
                async for row in cursor:
                    children.append(
                        {
                            "id": row[0],
                            "content": row[1],
                            "type": row[2],
                            "created_at": row[3],
                            "updated_at": row[4],
                        }
                    )
        return children

    async def delete_block(self, block_id: str) -> bool:
        """Delete a block and all its links."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM links WHERE source_id = ? OR target_id = ?",
                (block_id, block_id),
            )
            await db.execute("DELETE FROM blocks WHERE id = ?", (block_id,))
            await db.commit()
            return True

    async def create_child_block(
        self,
        parent_id: str,
        content: str,
        block_type: str,
        block_id: Optional[str] = None,
    ) -> str:
        """Create a new block and link it as a child of the parent block."""
        child_id = await self.create_block(content, block_type, block_id)
        await self.link_blocks(parent_id, child_id)
        return child_id

    async def create_sibling_block(
        self,
        sibling_id: str,
        content: str,
        block_type: str,
        block_id: Optional[str] = None,
    ) -> Optional[str]:
        """Create a new block as a sibling (sharing the same parent)."""
        # Find the parent of the sibling
        async with self.db.execute(
            "SELECT source_id FROM links WHERE target_id = ?", (sibling_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None  # No parent found
            parent_id = row[0]

        # Create new block and link to the same parent
        return await self.create_child_block(parent_id, content, block_type, block_id)

    async def get_parent(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Get the parent block of the given block."""
        async with self.db.execute(
            """
            SELECT b.* FROM blocks b
            JOIN links l ON b.id = l.source_id
            WHERE l.target_id = ?
            """,
            (block_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "content": row[1],
                    "type": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                }
            return None

    async def get_siblings(self, block_id: str) -> List[Dict[str, Any]]:
        """Get all blocks that share the same parent."""
        parent = await self.get_parent(block_id)
        if not parent:
            return []
        siblings = await self.get_children(parent["id"])
        return [block for block in siblings if block["id"] != block_id]

    async def get_ancestors(self, block_id: str) -> List[Dict[str, Any]]:
        """Get all ancestors of a block in order from root to immediate parent."""
        ancestors = []
        current_id = block_id

        while True:
            parent = await self.get_parent(current_id)
            if not parent:
                break
            ancestors.insert(0, parent)  # Add to start to maintain root->leaf order
            current_id = parent["id"]

        return ancestors

    async def move_block(
        self, block_id: str, new_parent_id: str, position: int = -1
    ) -> bool:
        """Move a block to a new parent at the specified position."""
        # Check for cycles
        if await self.would_create_cycle(block_id, new_parent_id):
            return False

        async with self.db.execute(
            "DELETE FROM links WHERE target_id = ?", (block_id,)
        ):
            await self.db.commit()

        success = await self.link_blocks(new_parent_id, block_id)
        if success and position >= 0:
            # Implementation for position-based ordering would go here
            # This would require adding an 'order' column to the links table
            pass

        return success

    async def set_block_order(self, parent_id: str, child_ids: List[str]) -> bool:
        """Set the order of children for a given parent."""
        # Verify all blocks exist and are children of parent
        current_children = await self.get_children(parent_id)
        current_child_ids = {child["id"] for child in current_children}

        if not all(cid in current_child_ids for cid in child_ids):
            return False

        # Implementation for ordering would go here
        # This would require adding an 'order' column to the links table
        return True

    async def get_connected_blocks(
        self,
        start_id: str,
        max_distance: int = -1,
        block_types: Optional[List[str]] = None,
        since: Optional[Union[datetime, timedelta]] = None,
        include_refs: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get all blocks connected to the start block within given constraints."""
        visited = set()
        result = []
        queue = deque([(start_id, 0)])  # (block_id, distance)

        while queue:
            current_id, distance = queue.popleft()
            if current_id in visited:
                continue

            if max_distance >= 0 and distance > max_distance:
                continue

            visited.add(current_id)
            block = await self.get_block(current_id)
            if not block:
                continue

            if not block_types or block["type"] in block_types:
                result.append(block)

            # Get connected blocks
            if include_refs:
                # Add reference connections
                async with self.db.execute(
                    "SELECT target_id FROM block_references WHERE source_id = ?",
                    (current_id,),
                ) as cursor:
                    refs = await cursor.fetchall()
                    for ref in refs:
                        if ref[0] not in visited:
                            queue.append((ref[0], distance + 1))

                async with self.db.execute(
                    "SELECT source_id FROM block_references WHERE target_id = ?",
                    (current_id,),
                ) as cursor:
                    backrefs = await cursor.fetchall()
                    for ref in backrefs:
                        if ref[0] not in visited:
                            queue.append((ref[0], distance + 1))

            # Always process direct tree connections
            children = await self.get_children(current_id)
            for child in children:
                if child["id"] not in visited:
                    queue.append((child["id"], distance + 1))

        return result

    async def _traverse_tree(
        self,
        block_id: str,
        max_distance: int = -1,
        distance: int = 0,
        visited: Optional[Set[str]] = None,
    ) -> Set[str]:
        """Helper method to traverse tree and collect block IDs within distance."""
        if visited is None:
            visited = set()

        if max_distance >= 0 and distance > max_distance:
            return visited

        visited.add(block_id)

        # Get direct children
        children = await self.get_children(block_id)
        for child in children:
            if child["id"] not in visited:
                await self._traverse_tree(
                    child["id"], max_distance, distance + 1, visited
                )

        return visited

    async def get_graph(
        self,
        root_id: Optional[str] = None,
        max_distance: int = -1,
        block_types: Optional[List[str]] = None,
        since: Optional[Union[datetime, timedelta]] = None,
    ) -> Dict[str, Any]:
        """Generate a graph representation of connected blocks."""
        nodes = []
        edges = set()  # Using set to avoid duplicate edges

        # Get connected blocks
        if root_id:
            block_ids = await self._traverse_tree(root_id, max_distance)
        else:
            async with self.db.execute("SELECT id FROM blocks") as cursor:
                block_ids = {row[0] async for row in cursor}

        # Filter blocks and collect nodes
        filtered_ids = set()
        for block_id in block_ids:
            block = await self.get_block(block_id)
            if block:
                if block_types and block["type"] not in block_types:
                    continue
                if since:
                    since_dt = (
                        since if isinstance(since, datetime) else datetime.now() - since
                    )
                    if datetime.fromisoformat(block["updated_at"]) < since_dt:
                        continue
                filtered_ids.add(block_id)
                nodes.append(block)

        # Collect edges
        for block_id in filtered_ids:
            # Add direct links
            async with self.db.execute(
                """
                SELECT source_id, target_id FROM links 
                WHERE (source_id = ? OR target_id = ?) 
                AND source_id IN ({0}) AND target_id IN ({0})
                """.format(
                    ",".join("?" * len(filtered_ids))
                ),
                (block_id, block_id, *filtered_ids, *filtered_ids),
            ) as cursor:
                async for row in cursor:
                    edges.add((row[0], row[1], "link"))

            # Add reference edges
            async with self.db.execute(
                """
                SELECT source_id, target_id FROM block_references 
                WHERE (source_id = ? OR target_id = ?)
                AND source_id IN ({0}) AND target_id IN ({0})
                """.format(
                    ",".join("?" * len(filtered_ids))
                ),
                (block_id, block_id, *filtered_ids, *filtered_ids),
            ) as cursor:
                async for row in cursor:
                    edges.add((row[0], row[1], "reference"))

        return {
            "nodes": nodes,
            "edges": [
                {"source": s, "target": t, "type": type_} for s, t, type_ in edges
            ],
        }

    async def get_rich_graph(
        self,
        block_ids: Union[str, List[str]],
        max_distance: int = 1,
        include_refs: bool = True,
    ) -> Dict[str, Any]:
        """Generate a rich connection graph for one or more blocks."""
        if isinstance(block_ids, str):
            block_ids = [block_ids]

        visited_blocks: Dict[str, Dict[str, Any]] = {}
        edges: Set[Tuple[str, str, str, str]] = set()
        visited = set()  # Track visited for traversal

        for start_id in block_ids:
            queue = deque([(start_id, 0)])

            while queue:
                current_id, depth = queue.popleft()
                if current_id in visited:
                    continue

                if max_distance >= 0 and depth > max_distance:
                    continue

                visited.add(current_id)

                # Get block info
                block = await self.get_block(current_id)
                if not block:
                    continue

                # Store node info
                if (
                    current_id not in visited_blocks
                    or depth < visited_blocks[current_id]["depth"]
                ):
                    children = await self.get_children(current_id)
                    refs = await self.get_backlinks(current_id) if include_refs else []
                    parent = await self.get_parent(current_id)

                    visited_blocks[current_id] = {
                        **block,
                        "depth": depth,
                        "ref_count": len(refs),
                        "child_count": len(children),
                        "parent_count": 1 if parent else 0,
                    }

                    # Add edges only within max_distance
                    if max_distance < 0 or depth < max_distance:
                        # Add child edges
                        for child in children:
                            edges.add((current_id, child["id"], "link", "outgoing"))
                            if child["id"] not in visited:
                                queue.append((child["id"], depth + 1))

                        # Add reference edges
                        if include_refs:
                            # Outgoing references
                            async with self.db.execute(
                                "SELECT target_id FROM block_references WHERE source_id = ?",
                                (current_id,),
                            ) as cursor:
                                refs = await cursor.fetchall()
                                for ref in refs:
                                    edges.add(
                                        (current_id, ref[0], "reference", "outgoing")
                                    )
                                    if ref[0] not in visited and (
                                        max_distance < 0 or depth + 1 <= max_distance
                                    ):
                                        queue.append((ref[0], depth + 1))

                            # Incoming references
                            async with self.db.execute(
                                "SELECT source_id FROM block_references WHERE target_id = ?",
                                (current_id,),
                            ) as cursor:
                                backrefs = await cursor.fetchall()
                                for ref in backrefs:
                                    edges.add(
                                        (ref[0], current_id, "reference", "incoming")
                                    )
                                    if ref[0] not in visited and (
                                        max_distance < 0 or depth + 1 <= max_distance
                                    ):
                                        queue.append((ref[0], depth + 1))

        return {
            "nodes": list(visited_blocks.values()),
            "edges": [
                {"source": s, "target": t, "type": type_, "direction": direction}
                for s, t, type_, direction in edges
            ],
        }

    async def get_graph_svg(
        self,
        block_ids: Union[str, List[str]],
        max_distance: int = 1,
        include_refs: bool = True,
        **kwargs,
    ) -> str:
        """Generate an SVG visualization of the block graph."""
        graph_data = await self.get_rich_graph(block_ids, max_distance, include_refs)

        # Create digraph with modern styling
        dot = Digraph(
            comment="Block Graph",
            format="svg",
            encoding="utf-8",
            graph_attr={
                "rankdir": "TB",
                "splines": "polyline",  # Cleaner lines
                "bgcolor": "transparent",
                "charset": "utf-8",
                "pad": "0.5",
                "nodesep": "0.75",
                "ranksep": "0.75",
            },
            node_attr={
                "shape": "rect",
                "style": "rounded,filled",
                "fillcolor": "#ffffff",
                "fontname": "Inter, Arial, sans-serif",
                "fontsize": "11",
                "height": "0.4",
                "width": "0.4",
                "margin": "0.2,0.1",  # Compact nodes
                "penwidth": "1.2",
            },
            edge_attr={
                "fontname": "Inter, Arial, sans-serif",
                "fontsize": "9",
                "penwidth": "0.8",
                "arrowsize": "0.7",
            },
        )

        # Subtle, modern color palette
        node_style = {
            "note": {"fillcolor": "#f8fafc", "color": "#64748b"},
            "task": {"fillcolor": "#f8fafc", "color": "#64748b"},
            "default": {"fillcolor": "#f8fafc", "color": "#64748b"},
        }
        edge_style = {
            "link": {"color": "#cbd5e1", "style": "solid"},
            "reference": {"color": "#e2e8f0", "style": "dashed"},
            "default": {"color": "#e2e8f0", "style": "dotted"},
        }

        # Override with custom styles
        if "node_style" in kwargs:
            node_style.update(kwargs["node_style"])
        if "edge_style" in kwargs:
            edge_style.update(kwargs["edge_style"])
        max_label_length = kwargs.get("max_label_length", 30)

        # Add nodes with sanitized labels
        for node in graph_data["nodes"]:
            # Sanitize label text
            label = node["content"][:max_label_length]
            label = label.encode("ascii", "replace").decode("ascii")
            if len(node["content"]) > max_label_length:
                label += "..."

            style = node_style.get(node["type"], node_style["default"])
            tooltip = f"{node['type']}\n{node['content']}"[:100]  # Limit tooltip length
            dot.node(node["id"], label, **style, tooltip=tooltip)

        # Add edges with minimal labels
        for edge in graph_data["edges"]:
            style = edge_style.get(edge["type"], edge_style["default"])
            dot.edge(edge["source"], edge["target"], **style)

        try:
            # Try to get SVG with UTF-8 encoding
            svg_bytes = dot.pipe(encoding="utf-8")
            return svg_bytes
        except UnicodeDecodeError:
            # Fallback to latin1 if UTF-8 fails
            return dot.pipe().decode("latin1")
