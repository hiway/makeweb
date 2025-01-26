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


async def test_edit_block(journal):
    """Test editing a block's content."""
    block_id = await journal.create_block("Original content", "note")

    # Edit the block
    success = await journal.edit_block(block_id, "Updated content")
    assert success is True

    # Verify the update
    block = await journal.get_block(block_id)
    assert block["content"] == "Updated content"


async def test_block_metadata(journal):
    """Test setting and getting block metadata."""
    block_id = await journal.create_block("Test block", "note")

    # Set metadata
    await journal.set_metadata(block_id, "status", "draft")
    await journal.set_metadata(block_id, "tags", "test,demo")

    # Get specific metadata
    status = await journal.get_metadata(block_id, "status")
    assert status == {"status": "draft"}

    # Get all metadata
    metadata = await journal.get_metadata(block_id)
    assert metadata == {"status": "draft", "tags": "test,demo"}


async def test_search_blocks(journal):
    """Test full-text search functionality."""
    # Create test blocks
    await journal.create_block("Apple pie recipe", "note")
    await journal.create_block("Banana bread recipe", "note")
    await journal.create_block("Shopping list", "todo")

    # Search for recipes
    results = await journal.search_blocks("recipe")
    assert len(results) == 2
    assert all("recipe" in block["content"] for block in results)


async def test_backlinks(journal):
    """Test backlinks functionality."""
    # Create target block first
    target_id = await journal.create_block("Target block", "note")

    # Create blocks that reference the target
    source1_id = await journal.create_block(f"Reference to [[Target block]]", "note")
    source2_id = await journal.create_block(
        f"Another [[Target block]] reference", "note"
    )

    # Get backlinks
    backlinks = await journal.get_backlinks(target_id)
    assert len(backlinks) == 2
    assert all(b["id"] in [source1_id, source2_id] for b in backlinks)

    # Test reference context
    contexts = [b["context"] for b in backlinks]
    assert "Target block" in contexts


async def test_get_connected_blocks(journal):
    """Test retrieving connected blocks with filters."""
    # Create a network of blocks
    root_id = await journal.create_block("Root", "note")
    child1_id = await journal.create_child_block(root_id, "Child 1", "task")
    child2_id = await journal.create_child_block(root_id, "Child 2", "note")
    grandchild_id = await journal.create_child_block(
        child1_id, "[[Child 2]] reference", "note"
    )

    # Test basic connectivity
    blocks = await journal.get_connected_blocks(root_id, include_refs=False)
    assert len(blocks) == 4  # root + child1 + child2 + grandchild
    block_ids = {b["id"] for b in blocks}
    assert block_ids == {root_id, child1_id, child2_id, grandchild_id}

    # Test distance limit
    blocks = await journal.get_connected_blocks(root_id, max_distance=1)
    assert len(blocks) == 3  # root + 2 children

    # Test type filter
    blocks = await journal.get_connected_blocks(root_id, block_types=["task"])
    assert len(blocks) == 1
    assert blocks[0]["id"] == child1_id

    # Test reference inclusion
    blocks = await journal.get_connected_blocks(child2_id, include_refs=True)
    assert len(blocks) == 2  # child2 + grandchild (via reference)
    block_ids = {b["id"] for b in blocks}
    assert block_ids == {child2_id, grandchild_id}

    # Test with both tree and reference traversal
    blocks = await journal.get_connected_blocks(root_id, include_refs=True)
    assert len(blocks) == 4  # Same blocks, just includes reference connections
    block_ids = {b["id"] for b in blocks}
    assert block_ids == {root_id, child1_id, child2_id, grandchild_id}


async def test_get_graph(journal):
    """Test generating graph representation."""
    # Create a network of blocks
    root_id = await journal.create_block("Root", "note")
    child1_id = await journal.create_child_block(root_id, "Child 1", "note")
    child2_id = await journal.create_child_block(root_id, "Child 2", "note")
    await journal.create_block("[[Child 1]] links to [[Child 2]]", "note")

    # Get full graph
    graph = await journal.get_graph()
    assert len(graph["nodes"]) >= 4

    # Verify edge types
    link_edges = [e for e in graph["edges"] if e["type"] == "link"]
    ref_edges = [e for e in graph["edges"] if e["type"] == "reference"]
    assert len(link_edges) >= 2  # At least 2 parent-child links
    assert len(ref_edges) >= 2  # At least 2 reference links

    # Test subgraph from root
    subgraph = await journal.get_graph(root_id, max_distance=1)
    assert len(subgraph["nodes"]) == 3  # root + 2 children


async def test_rich_graph_generation(journal):
    """Test rich graph generation with various configurations."""
    # Create a test network
    root_id = await journal.create_block("Root", "note")
    child1_id = await journal.create_child_block(root_id, "Child 1", "task")
    child2_id = await journal.create_child_block(root_id, "Child 2", "note")
    grandchild_id = await journal.create_child_block(
        child1_id, "[[Child 2]] reference", "note"
    )

    # Test single block graph with no references
    graph = await journal.get_rich_graph(root_id, max_distance=1, include_refs=False)
    assert len(graph["nodes"]) == 3  # root + 2 children
    assert len(graph["edges"]) == 2  # 2 parent-child links

    # Test complete graph with references
    graph = await journal.get_rich_graph(root_id, max_distance=2, include_refs=True)
    assert len(graph["nodes"]) == 4  # all blocks
    assert len(graph["edges"]) == 4  # 3 tree links + 1 reference

    # Test node attributes
    root_node = next(n for n in graph["nodes"] if n["id"] == root_id)
    assert root_node["child_count"] == 2
    assert root_node["parent_count"] == 0

    # Verify edge types
    link_edges = [e for e in graph["edges"] if e["type"] == "link"]
    ref_edges = [e for e in graph["edges"] if e["type"] == "reference"]
    assert len(link_edges) == 3  # root->child1, root->child2, child1->grandchild
    assert len(ref_edges) == 1  # grandchild->child2

    # Test SVG generation
    svg = await journal.get_graph_svg(root_id, max_distance=1)
    assert svg.startswith("<?xml")
    assert "svg" in svg
