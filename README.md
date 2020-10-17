# Landslide EarlyDetection
Machine Learning Research Project: Landslide Risk based Early Detection

## Data

| nombre | fuente | tipo | url | formato | notebook | TODOs |
|--------|--------|------|-----|---------|----------|-------|
|        |        |      |     |         |          |       |
|        |        |      |     |         |          |       |
|        |        |      |     |         |          |       |


## Google Compute Engine

### Bucket

url : `gs://data-projectx`

```{Python}
!pip install fsspec
!pip install gcsfs

import fsspec

fs = fsspec.get_mapper('gcs://data-projectx/')

# show files
print(list(fs))

# access files
with fs.open(path, mode='rb', cache_type='readahead') as f:
  use_for_something(f)
```

* Tutorial access see notebook example (TODO)
* [ffsspec docs](https://readthedocs.org/projects/filesystem-spec/downloads/pdf/latest/)

### Free Access to TPUs

Step se consiguió TPUs gratis. Todavía no las prueba. El que se ofrezca a explorar esto bienvenido.
Solicitar info a Step.


## DescartesLab

Gives access to satellite data and `Workbench` (4vCPUs, 13GB~RAM, optional GPU)

### Credentials

If you need to access DescartesLab ask Step, Tomas or José

### Data Sources

| nombre |   id   | url  | formato | notebook | TODOs    |
|--------|--------|------|---------|----------|----------|
|        |        |      |         |          |          |
|        |        |      |         |          |          |
|        |        |      |         |          |          |
