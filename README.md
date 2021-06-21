#Usage - the same as usual

Virtualenv:

```
python3 -m venv .venv
```

# Start the wiremock in standalone mode

**NOTE: run in a separated console and not in background to see the logs**
```
./start.sh
```

# Load the static WSDL definitions mappings

**NOTE: activate the virtual environment 1rst**

```
source .venv/bin/activate
```

**Load the mappings** 

```
inv setup-static-mappings
```

# Run the sequential tests 


```
python -m pytest -v
```


# Run the test in parallel 

**using pytest-parallel** 


```
pytest --workers auto
```

or

```
pytest --tests-per-worker 1
```
