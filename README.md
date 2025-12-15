# mcedu
Provides methods to query Minecraft Education's discovery/joincode API and to generate related tokens.

## Installation

### From PyPI

```shell
pip install mcedu
```

### From Github

```shell
pip install git+https://github.com/josef240/mcedu.git
```

### Build Locally

```shell
git clone https://github.com/josef240/mcedu.git
cd mcedu
python -m pip install setuptools, build
python -m build
```

## Usage Example

```python
from mcedu.discovery import DiscoveryClient,WorldParams, parseJoinCode
from mcedu.config import get_config, easyStartup
from mcedu.auth import AuthFlow

auth=easyStartup()
config=get_config()

config.saveSettings()
discovery=DiscoveryClient(auth.mstoken)
ServerToken,JoinCode=discovery.host(WorldParams(nethernetID=67212867493148092771))
print(parseJoinCode(JoinCode))
```