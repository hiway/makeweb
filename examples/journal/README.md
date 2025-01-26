# Journal

A graph-based journaling system that allows creating and linking blocks of content.

## Features

- Create blocks with custom content and types
- Link blocks to create relationships
- Prevent cyclic relationships
- Retrieve blocks and their relationships
- Delete blocks and their links
- Custom block IDs support
- Rich graph generation with visualization
- Block metadata features
- Advanced search capabilities
- Block references and backlinks
- SVG graph visualization

## API Reference

### Initialization

```python
from journal import Journal

# Create a journal with in-memory database
journal = Journal()

# Or with a file-based database
journal = Journal("my_journal.db")

# Initialize the database (creates tables)
await journal.initialize()
```

### Creating Blocks

```python
# Create a block with auto-generated ID
block_id = await journal.create_block("My content", "note")

# Create a block with custom ID
custom_id = await journal.create_block("Custom ID block", "note", block_id="custom-123")
```

### Linking Blocks

```python
# Create a relationship between blocks
success = await journal.link_blocks(parent_id, child_id)

# The system prevents cyclic relationships
# A -> B -> C -> A would return False
```

### Creating Related Blocks

```python
# Create a child block (creates and links in one step)
child_id = await journal.create_child_block(parent_id, "Child content", "note")

# Create a sibling block (shares same parent)
sibling_id = await journal.create_sibling_block(existing_child_id, "Sibling content", "note")
```

### Retrieving Blocks

```python
# Get a single block
block = await journal.get_block(block_id)
# Returns: {
#     "id": str,
#     "content": str,
#     "type": str,
#     "created_at": timestamp,
#     "updated_at": timestamp
# }

# Get child blocks
children = await journal.get_children(block_id)
# Returns: List of block dictionaries
```

### Tree Navigation

```python
# Get parent of a block
parent = await journal.get_parent(block_id)

# Get siblings of a block
siblings = await journal.get_siblings(block_id)

# Get ancestors (from root to immediate parent)
ancestors = await journal.get_ancestors(block_id)
```

### Tree Manipulation

```python
# Move a block to a new parent
success = await journal.move_block(block_id, new_parent_id)

# Move a block to a specific position under new parent
success = await journal.move_block(block_id, new_parent_id, position=2)

# Set specific order of children under a parent
success = await journal.set_block_order(parent_id, [child1_id, child2_id, child3_id])
```

### Deleting Blocks

```python
# Delete a block and its relationships
success = await journal.delete_block(block_id)
```

### Block Updates and Search

```python
# Update block content
await journal.edit_block(block_id, "Updated content")

# Change block type
await journal.change_block_type(block_id, "todo")

# Search blocks
results = await journal.search_blocks("search query")
```

### Metadata and Tags

```python
# Set metadata
await journal.set_metadata(block_id, "status", "draft")
await journal.set_metadata(block_id, "tags", "important,todo")

# Get specific metadata
status = await journal.get_metadata(block_id, "status")

# Get all metadata
metadata = await journal.get_metadata(block_id)
```

### Backlinks

```python
# Get all blocks that reference this block
backlinks = await journal.get_backlinks(block_id)
for link in backlinks:
    print(f"Referenced in: {link['content']} (context: {link['context']})")
```

### Graph Visualization

```python
# Generate SVG graph of the journal
svg = await journal.generate_svg()
with open("journal_graph.svg", "w") as f:
    f.write(svg)
```

## Data Structure

### Blocks Table

- `id`: Text (Primary Key)
- `content`: Text
- `type`: Text
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Links Table

- `source_id`: Text (Foreign Key -> blocks.id)
- `target_id`: Text (Foreign Key -> blocks.id)
- `type`: Text
- `created_at`: Timestamp

## Implementation Details

- Uses SQLite as the backing store via aiosqlite
- Async/await interface for all operations
- Enforces referential integrity
- Prevents cyclic relationships using depth-first search
- Auto-generates UUIDs for blocks when ID not provided

## Example Usage

```python
# Initialize journal
journal = Journal("my_journal.db")
await journal.initialize()

# Create some blocks
root_id = await journal.create_block("Root note", "note")
child1_id = await journal.create_block("Child note 1", "note")
child2_id = await journal.create_block("Child note 2", "note")

# Create relationships
await journal.link_blocks(root_id, child1_id)
await journal.link_blocks(root_id, child2_id)

# Retrieve children
children = await journal.get_children(root_id)
for child in children:
    print(f"Child block: {child['content']}")

# Create root block
root_id = await journal.create_block("Root note", "note")

# Create children directly
child1_id = await journal.create_child_block(root_id, "First child", "note")
child2_id = await journal.create_child_block(root_id, "Second child", "note")

# Create a sibling
sibling_id = await journal.create_sibling_block(child1_id, "Sibling to first child", "note")

# Clean up
await journal.disconnect()
```

## Example: Complex Tree Operations

```python
# Create a hierarchical structure
root_id = await journal.create_block("Root", "note")
section1_id = await journal.create_child_block(root_id, "Section 1", "note")
section2_id = await journal.create_child_block(root_id, "Section 2", "note")
subsection_id = await journal.create_child_block(section1_id, "Subsection", "note")

# Move subsection from section1 to section2
await journal.move_block(subsection_id, section2_id)

# Get the complete path to a block
ancestors = await journal.get_ancestors(subsection_id)
path = " > ".join(block["content"] for block in ancestors)
# Result: "Root > Section 2"

# Get siblings of a block
siblings = await journal.get_siblings(subsection_id)
```

## Development

### Running Tests

```bash
pytest tests/
```
