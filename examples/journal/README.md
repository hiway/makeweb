# Journal

A graph-based journaling system that allows creating and linking blocks of content.

## Features

- Create blocks with custom content and types
- Link blocks to create relationships
- Prevent cyclic relationships
- Retrieve blocks and their relationships
- Delete blocks and their links
- Custom block IDs support

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

### Deleting Blocks

```python
# Delete a block and its relationships
success = await journal.delete_block(block_id)
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

## Development

### Running Tests

```bash
pytest tests/
```
