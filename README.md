# Termination tests for universal bindgins

## Local run
### Verify that you have python installed in system
```
python -V
```

### Install deps
```
pyhon -m pip install -r requirements.txt
```

### Run test on your platform
```
pytest test_usdk_terminates.py
```

## Add new binding
Create binding with lang name inside `bindings` folder.
Add your binding there and add info to `TEST_VARIANTS` const.