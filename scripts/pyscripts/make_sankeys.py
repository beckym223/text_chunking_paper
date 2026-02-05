import pandas as pd
import re
from plotly import graph_objects as go
import os
import json
from typing import List, Dict, Tuple,Any, Optional,Callable

from utils.constants import CHUNK_DISPLAY_NAMES, JSON_DATA_PATH
from utils.plot_utils import make_save_sankey


### Helper functions

def wrap_label(label,n_to_wrap=3):
    pattern = r"((?:\w+(?:,|:)\s?){%d})\s" % n_to_wrap
    return "<b>"+re.sub(pattern,"\\1<br>",label)

def get_model_title(model_id:str)->str:
    chunk_name,k = re.match(r"([\w\d]+?)_(\d+)k",model_id).groups(default=('err',-1))
    return f"<b>{CHUNK_DISPLAY_NAMES.get(chunk_name,"NA").title()}<br>K={k}"



def main():

    json_paths = [f for f in os.listdir(JSON_DATA_PATH) if f.endswith(".json")]

    for j in json_paths:

        full_path = os.path.join(JSON_DATA_PATH,j)
        
        with open(full_path, 'r') as f:
            data = json.load(f)
            model_path = data["model_ids"]
            top_titles = [get_model_title(t) for t in model_path]
            num_models = len(model_path)

            add_extra_col = num_models>2
            links = data['data']['links']
            nodes = data['data']['nodes']
            nodes['path_idx'] = [model_path.index(m) for m in nodes['model_id']]
            nodes['label_wrapped'] = [wrap_label(l) for l in nodes['label']]


        # end open file
    




if __name__ == "__main__":
    main()
# end main



