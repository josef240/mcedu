"This is where general utility functions will go."
from uuid import uuid4

uuid=lambda: str(uuid4())
paramstring=lambda l: ",".join([x for x in l if x!=""])
paramaker=lambda x,y: f"{x}={y}"