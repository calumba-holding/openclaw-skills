# references/examples.md — usage examples

## Example 1: round-trip

```python
doc = load("in.txt")
save(doc, "out.txt")
```

## Example 2: merge

```python
a = load("a.txt")
b = load("b.txt")
merged = merge(a, b)
save(merged, "combined.txt")
```

These examples are purely illustrative — the functions don't exist in this demo skill.
