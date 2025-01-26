import os
import pytest
from journal import Journal

TEST_DB = "test_journal.db"


@pytest.fixture
async def journal():
    """Create a test journal instance."""
    journal = Journal(TEST_DB)
    await journal.initialize()

    yield journal  # Use yield for async fixtures

    # Cleanup after the test
    await journal.disconnect()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


async def test_create_and_get_block(journal):
    """Test creating and retrieving a block."""
    content = "Test block content"
    block_type = "note"

    # Create block
    block_id = await journal.create_block(content, block_type)
    assert block_id is not None

    # Retrieve block
    block = await journal.get_block(block_id)
    assert block is not None
    assert block["content"] == content
    assert block["type"] == block_type


async def test_link_blocks(journal):
    """Test linking two blocks."""
    # Create two blocks
    block1_id = await journal.create_block("Parent block", "note")
    block2_id = await journal.create_block("Child block", "note")

    # Link them
    success = await journal.link_blocks(block1_id, block2_id)
    assert success is True

    # Get children
    children = await journal.get_children(block1_id)
    assert len(children) == 1
    assert children[0]["id"] == block2_id


async def test_cycle_prevention(journal):
    """Test that cycles are prevented."""
    # Create three blocks
    block1_id = await journal.create_block("Block 1", "note")
    block2_id = await journal.create_block("Block 2", "note")
    block3_id = await journal.create_block("Block 3", "note")

    # Create a chain: 1 -> 2 -> 3
    assert await journal.link_blocks(block1_id, block2_id)
    assert await journal.link_blocks(block2_id, block3_id)

    # Attempt to create a cycle: 3 -> 1
    success = await journal.link_blocks(block3_id, block1_id)
    assert success is False


async def test_delete_block(journal):
    """Test deleting a block and its links."""
    # Create and link blocks
    parent_id = await journal.create_block("Parent", "note")
    child1_id = await journal.create_block("Child 1", "note")
    child2_id = await journal.create_block("Child 2", "note")

    await journal.link_blocks(parent_id, child1_id)
    await journal.link_blocks(parent_id, child2_id)

    # Delete parent
    success = await journal.delete_block(parent_id)
    assert success is True

    # Verify parent is gone
    parent = await journal.get_block(parent_id)
    assert parent is None

    # Verify children still exist but are unlinked
    child1 = await journal.get_block(child1_id)
    assert child1 is not None

    # Verify no children are linked
    children = await journal.get_children(parent_id)
    assert len(children) == 0


async def test_block_with_custom_id(journal):
    """Test creating a block with a custom ID."""
    custom_id = "custom-123"
    block_id = await journal.create_block("Test content", "note", block_id=custom_id)
    assert block_id == custom_id

    block = await journal.get_block(custom_id)
    assert block is not None
    assert block["id"] == custom_id


async def test_multiple_children(journal):
    """Test retrieving multiple children of a block."""
    parent_id = await journal.create_block("Parent", "note")
    child_ids = []

    # Create and link 5 children
    for i in range(5):
        child_id = await journal.create_block(f"Child {i}", "note")
        child_ids.append(child_id)
        await journal.link_blocks(parent_id, child_id)

    children = await journal.get_children(parent_id)
    assert len(children) == 5
    assert all(child["id"] in child_ids for child in children)


async def test_create_child_block(journal):
    """Test creating a child block."""
    parent_id = await journal.create_block("Parent", "note")
    child_id = await journal.create_child_block(parent_id, "Child", "note")

    # Verify child was created and linked
    children = await journal.get_children(parent_id)
    assert len(children) == 1
    assert children[0]["id"] == child_id
    assert children[0]["content"] == "Child"


async def test_create_sibling_block(journal):
    """Test creating a sibling block."""
    # Create parent and first child
    parent_id = await journal.create_block("Parent", "note")
    first_child_id = await journal.create_child_block(parent_id, "First Child", "note")

    # Create sibling
    sibling_id = await journal.create_sibling_block(first_child_id, "Sibling", "note")

    # Verify both children are linked to parent
    children = await journal.get_children(parent_id)
    assert len(children) == 2
    child_ids = [child["id"] for child in children]
    assert first_child_id in child_ids
    assert sibling_id in child_ids


async def test_create_sibling_without_parent(journal):
    """Test creating a sibling for a block without parent."""
    # Create orphan block
    orphan_id = await journal.create_block("Orphan", "note")

    # Attempt to create sibling
    sibling_id = await journal.create_sibling_block(orphan_id, "Sibling", "note")
    assert sibling_id is None


async def test_get_parent(journal):
    """Test retrieving a block's parent."""
    parent_id = await journal.create_block("Parent", "note")
    child_id = await journal.create_child_block(parent_id, "Child", "note")

    parent = await journal.get_parent(child_id)
    assert parent is not None
    assert parent["id"] == parent_id
    assert parent["content"] == "Parent"

    # Test with root block (no parent)
    root_parent = await journal.get_parent(parent_id)
    assert root_parent is None


async def test_get_siblings(journal):
    """Test retrieving a block's siblings."""
    parent_id = await journal.create_block("Parent", "note")
    child1_id = await journal.create_child_block(parent_id, "Child 1", "note")
    child2_id = await journal.create_child_block(parent_id, "Child 2", "note")
    child3_id = await journal.create_child_block(parent_id, "Child 3", "note")

    # Get siblings of child2
    siblings = await journal.get_siblings(child2_id)
    assert len(siblings) == 2
    sibling_ids = {s["id"] for s in siblings}
    assert child1_id in sibling_ids
    assert child3_id in sibling_ids
    assert child2_id not in sibling_ids

    # Test with root block (no siblings)
    root_siblings = await journal.get_siblings(parent_id)
    assert len(root_siblings) == 0


async def test_get_ancestors(journal):
    """Test retrieving a block's ancestors."""
    # Create a chain: root -> parent -> child -> grandchild
    root_id = await journal.create_block("Root", "note")
    parent_id = await journal.create_child_block(root_id, "Parent", "note")
    child_id = await journal.create_child_block(parent_id, "Child", "note")
    grandchild_id = await journal.create_child_block(child_id, "Grandchild", "note")

    # Get ancestors of grandchild
    ancestors = await journal.get_ancestors(grandchild_id)
    assert len(ancestors) == 3
    assert ancestors[0]["id"] == root_id  # First ancestor should be root
    assert ancestors[1]["id"] == parent_id
    assert ancestors[2]["id"] == child_id

    # Test with root block (no ancestors)
    root_ancestors = await journal.get_ancestors(root_id)
    assert len(root_ancestors) == 0


async def test_move_block(journal):
    """Test moving a block to a new parent."""
    # Create initial structure
    root1_id = await journal.create_block("Root 1", "note")
    root2_id = await journal.create_block("Root 2", "note")
    child_id = await journal.create_child_block(root1_id, "Child", "note")

    # Move child from root1 to root2
    success = await journal.move_block(child_id, root2_id)
    assert success is True

    # Verify child was moved
    assert len(await journal.get_children(root1_id)) == 0
    children = await journal.get_children(root2_id)
    assert len(children) == 1
    assert children[0]["id"] == child_id

    # Test cycle prevention
    child2_id = await journal.create_child_block(child_id, "Child 2", "note")
    success = await journal.move_block(root2_id, child2_id)
    assert success is False


async def test_complex_tree_operations(journal):
    """Test a complex sequence of tree operations."""
    # Create initial structure
    root_id = await journal.create_block("Root", "note")
    child1_id = await journal.create_child_block(root_id, "Child 1", "note")
    child2_id = await journal.create_child_block(root_id, "Child 2", "note")
    grandchild_id = await journal.create_child_block(child1_id, "Grandchild", "note")

    # Move grandchild to be child of child2
    await journal.move_block(grandchild_id, child2_id)

    # Verify new structure
    assert len(await journal.get_children(child1_id)) == 0
    assert len(await journal.get_children(child2_id)) == 1

    # Verify ancestors
    ancestors = await journal.get_ancestors(grandchild_id)
    assert len(ancestors) == 2
    assert ancestors[0]["id"] == root_id
    assert ancestors[1]["id"] == child2_id
