# Debugging Report

## 1. Bug Description
The system allows developers to register different cloud resources. A resource can optionally be assigned a list of tags (e.g., `['environment:production', 'team:backend']`). 

When we add the tag `'environment:production'` to our `web-server-01` instance, the tag magically and unintentionally appears on our `database-server-01` and `company-assets-bucket` instances as well. 

## 2. Expected Result
Tags added to a specific object instance (e.g., `web_server.add_tag(...)`) should only modify the state of that specific instance. 

## 3. Actual Result
Adding a tag to the `web_server` object inadvertently adds the tag to all other resources that were initialized without an explicit `tags` argument. 

[INSERT SCREENSHOT: Bug Manifestation]
*(A screenshot showing the terminal output where printing tags for the web server, db server, and bucket all show `['environment:production']`)*

## 4. Root Cause Analysis
The bug resides in `models/base_resource.py` inside the `CloudResource` initialization method:

```python
def __init__(self, resource_id: str, name: str, region: str, tags: list = []):
    ...
    self._tags = tags
```

This is a classic Python anti-pattern known as a **Mutable Default Argument**. In Python, default arguments are evaluated *exactly once* when the function definition is executed (at import/compile time), not each time the function is called. 

Because `[]` is a mutable list object, every time `ComputeInstance(...)` or `StorageBucket(...)` is instantiated without providing a `tags` argument, they are assigned a reference to the **exact same list object in memory**. When `web_server.add_tag()` appends a string to this list, all other objects referencing that same list see the change.

## 5. Debugging Process

### Step 1: Reproducing the issue
Running `main.py` clearly outputs:
```text
202X-XX-XX - __main__ - INFO - Adding 'environment:production' tag to web_server only...
202X-XX-XX - __main__ - INFO - Tags for web_server: ['environment:production']
202X-XX-XX - __main__ - INFO - Tags for db_server (Unexpectedly has the tag!): ['environment:production']
```

[INSERT SCREENSHOT: Terminal output]

### Step 2: Isolating the State Mutation
To verify if the variables are referencing the same object in memory, I added `print(id(resource._tags))` for each object inside `main.py`.

```python
print(id(web_server._tags))    # Output: 140410657962112
print(id(db_server._tags))     # Output: 140410657962112
print(id(assets_bucket._tags)) # Output: 140410657962112
```

The matching memory addresses confirmed that they share the exact same underlying list instance.

### Step 3: Tracing back to instantiation
Tracing the `__init__` sequence from `main.py` -> `ComputeInstance.__init__` -> `CloudResource.__init__`, I identified the mutable default argument `tags: list = []` as the culprit.

[INSERT SCREENSHOT: Debugging session showing identical memory IDs]

## 6. Final Fix

To resolve this, the standard industry practice is to use `None` as the default value and initialize a new list inside the method body. This guarantees a new list object is created *every time* the method is called.

### Original Code (`models/base_resource.py`)
```python
class CloudResource(ABC):
    def __init__(self, resource_id: str, name: str, region: str, tags: list = []):
        self._resource_id = resource_id
        self._name = name
        self._region = region
        self._tags = tags
```

### Corrected Code
```python
class CloudResource(ABC):
    def __init__(self, resource_id: str, name: str, region: str, tags: list = None):
        self._resource_id = resource_id
        self._name = name
        self._region = region
        # If no tags are provided, create a fresh, unique list for this instance
        self._tags = tags if tags is not None else []
```

### Explanation of why the fix works
By setting the default argument to `None` (an immutable singleton in Python), the function evaluation at compile time simply stores a reference to `None`. 
During each object instantiation, the `if tags is not None else []` expression executes dynamically. Every time `[]` is executed dynamically inside the function scope, Python allocates memory for a brand new, independent list, entirely resolving the shared state linkage.

[INSERT SCREENSHOT: Corrected execution showing different tags]
