# vsphere-automation-scripts
Scripts to automate boring vsphere operations

Scripts are derived from samples in [vsphere-automation-sdk-python](https://github.com/vmware/vsphere-automation-sdk-python)

You need to install prerequisites before running scripts, using virtual env is highly required:


```python3 -m venv .venv```

```source .venv/bin/activate```

```python3 -m pip  install --upgrade pip setuptools==60.10.0‍‍‍``` # Latest version had problems according to [issue 303](https://github.com/vmware/vsphere-automation-sdk-python/issues/303)

```python3 -m pip  install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git```

