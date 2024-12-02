## Test CMD

### Run Test 1

```python
python -m unittest test_db_connections.py
```

### Run Test 2

```python
python -m unittest test_transactions.py 
```

### Run Test 3

```python
python -m unittest test_data_validation.py
```

### Run All Tests

```python
python run_tests.py

python -m unittest discover -p "test_*.py"
```

### Automation of the Testes

```python
python run_tests.py > output.log 2>&1
```