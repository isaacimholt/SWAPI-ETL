# SWAPI ETL

The Star Wars API ETL

Goals of this exercise were to accomplish the given task while demonstrating the performance of asyncio-based solutions
and showing techniques for handling large datasets while keeping memory usage steady by way of "streaming" data with
generators.

Data is first acquired through asyncio-based aiohttp with a configurable limit on max connections, then normalized &
validated by way of the pydantic library. Additional data (such as species) is memoized using an asyncio-compatible LRU
cache. We then process the data using a heap queue to avoid keeping unnecessary data in memory. Pandas is used to
export the data to csv string, and finally we send it to HTTPBin.

Special care was made to treat this as a "production-grade" project, with all settings configurable from environment
variables, retry logic using the tenacity library, and double layer dependency management (in setup.py and
requirements.txt) using pip-tools. Optionally we might have separate production and test requirements lock files, but
in the interest of simplicity they are combined here.

This solution is (slightly) over-engineered with respect to the project requirements on purpose.

# Usage

1. Create venv python >= 3.11
2. pip install -r requirements.txt
3. python main.py (optionally set env vars for Settings)

# Dependency management

_create a venv first_

```bash
pip install pip --upgrade && pip install pip-tools --upgrade && pip-compile --extra=dev && pip-sync
```