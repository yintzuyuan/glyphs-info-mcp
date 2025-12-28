## [Optional Closing Lookup Name](#layout/optional-closing-lookup-name)

The standard feature syntax requires the name of a lookup to be repeated at the end of the lookup definition:

```python
lookup some_descriptive_lookup_name {
	# lookup code
} some_descriptive_lookup_name;

```

In Glyphs, the lookup name at the end may be omitted:

```python
lookup some_descriptive_lookup_name {
	# lookup code
};

```