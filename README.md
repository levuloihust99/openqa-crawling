# INSTALLATION GUIDE
This installation guide applies to Ubuntu 20.04
## Requirements
- Python 3.8
- MySQL 8.0.25

## Crawling data
### 1. Create virtual environment and install requirements
```shell
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt
```

### 2. Create MySQL database
```shell
$ sudo mysql -u root
mysql> CREATE DATABASE context_source;
mysql> CREATE USER 'yourname'@'%' IDENTIFIED BY 'openqathesis62021';
mysql> GRANT ALL ON context_source.* to 'yourname'@'%';
mysql> quit
```

### 3. Crawl data
#### 3.1 Crawl article links
- Uncomment lines from 28-32 in `run.py`
- Run crawling article links

```shell
$ PYTHONWARNINGS="ignore: Unverified HTTPS request" python run.py
```

#### 3.2 Crawl article contents
- Uncomment line 46
- Run crawling article contents

```shell
$ PYTHONWARNINGS="ignore: Unverified HTTPS request" python run.py
```