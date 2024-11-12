## Test CMD

### Run Test 1

```python
python -m unittest tests.test_db_mock
```

### Run Test 2

```python
python -m unittest tests.test_time_freeze
```

### Run Test 3

```python
python -m unittest tests.test_tdd
```

### Run All Tests

```python
python -m tests.run_tests
```

```python
python -m tests.run_tests --test-type db-mock --verbose
```

### Automation of the Testes

```python
python run_tests.py > output.log 2>&1
```

### Mutation Test

```python
python -m unittest tests/test_mutations.py -v
```
