"""
Implement Graph DB for Journal
"""

import aiosqlite
import asyncio
from datetime import datetime
from typing import List, Set, Optional, Dict, Any
from uuid import uuid4


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
        await self.db.commit()

    async def create_block(
        self, content: str, block_type: str, block_id: Optional[str] = None
    ) -> str:
        """Create a new block with optional ID (auto-generated if not provided)."""
        block_id = block_id or self.generate_id()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO blocks (id, content, type) VALUES (?, ?, ?)",
                    (block_id, content, block_type),
                )
                await db.commit()
                return block_id
        except aiosqlite.IntegrityError:
            if block_id:  # If provided ID conflicts, generate a new one
                return await self.create_block(content, block_type)
            raise

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
