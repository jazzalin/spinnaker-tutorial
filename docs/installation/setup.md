# Environment setup

In order to run simulations on the SpiNNaker using PyNN, we need to set up a development environment with the appropriate packages and configure the connection between the board and our work machine. In this tutorial, we will use PyNN with the NEST backend. Before installing the required python dependencies, the project repository should be cloned on the work machine. From the CLI,

```
git clone https://github.com/ljazzal/spinnaker-tutorial.git
```

## Installation
Before starting, it is important to have `python3.8` and `virtualenv` installed on the work machine. It is then easiest to set up a python virtual environment to ensure the correct project dependencies get installed. The virtual environment `venv` can be created locally with the following command

```
virtualenv -p /usr/bin/python3.8 venv
```

and activated

```
source venv/bin/activate
```

If the environment has been successfully activated, a `(venv)` will pre-pend the CLI.

## Network configuration

## NEST installation from source (Optional)