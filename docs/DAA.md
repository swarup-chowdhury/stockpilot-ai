# Algorithm Insights

**Merge Sort** orders products or sales records with a custom stable implementation. The business problem is deterministic ranking without claiming that a built-in sort is a custom algorithm. It recursively splits, sorts, and merges records. Best, average, and worst time are O(n log n); auxiliary space is O(n).

**Binary Search** finds an exact SKU in a list sorted by SKU. The sorted-data precondition is mandatory. Each comparison discards half the remaining range. Best case is O(1), average and worst case are O(log n), and iterative auxiliary space is O(1).

**Hash-based SKU lookup** maps SKU to a product dictionary for barcode/checkout resolution. Average lookup is O(1), with O(n) worst-case discussion for collisions; space is O(n). Database uniqueness prevents duplicate identifiers.

**Dijkstra's algorithm** evaluates the shortest distance over nonnegative warehouse route edges. It is a route-distance result, not a claim about historical delivery performance. Negative edges are rejected. With a binary heap, time is O((V+E) log V) and space is O(V+E).

**Priority queue** ranks restock alerts so critical stock gaps are surfaced before watch-level signals. Each alert is inserted into a heap and popped by severity and suggested quantity. Build-and-pop work is O(n log n), with O(n) space.

**FEFO** sorts positive-quantity batches by expiry and consumes the earliest expiry first. It protects perishable inventory and avoids treating expired positive quantity as sellable. Sorting is O(n log n), selection is O(n) after sorting, and auxiliary space is O(n).

Unit tests in `tests/test_core.py` cover sort order, binary-search behavior, negative-edge rejection, alert priority, FEFO selection, reorder calculations, Decimal totals, and insufficient stock rejection.
