## Test CMD

### Run Test 1
python -m unittest tests.test_db_mock

### Run Test 2
python -m unittest tests.test_time_freeze

### Run Test 3
python -m unittest tests.test_tdd

### Run All Tests
python -m tests.run_tests

python -m tests.run_tests --test-type db-mock --verbose


### Automation of the Testes
python run_tests.py > output.log 2>&1



