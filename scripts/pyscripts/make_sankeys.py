import pandas as pd
import re
from plotly import graph_objects as go 
from plotly.colors import qualitative as qc
import os
import json
from typing import List, Dict, Tuple,Any, Optional,Callable
from utils.constants import CHUNK_DISPLAY_NAMES, JSON_DATA_PATH
from utils.plot_utils import make_save_sankey

### Helper functions

def wrap_label(label,n_to_wrap=3):
    pattern = r"((?:\w+(?:,|:)\s?){%d})\s" % n_to_wrap
    return "<b>"+re.sub(pattern,"\\1<br>",label)

def wrap_title(title:str):
    return re.sub(": ","<br>",title)

def get_model_title(model_id:str)->str:
    m = re.match(r"([\w\d]+?)_(\d+)k",model_id)
    chunk_name,k = m.groups(default=('err',-1)) if m is not None else ('err',-1)
    chunk_title:str =CHUNK_DISPLAY_NAMES.get(chunk_name,'NA').title()#type:ignore
    return f"<b>{wrap_title(chunk_title)}<br>K={k}"

def hex_to_rgba(hex_color, alpha=0.85):
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'rgba({r},{g},{b},{alpha})'
    else:
        return 'rgba(0,0,0,0)'  # fallback
    
def add_extra_col(node_df:pd.DataFrame,
                  link_df:pd.DataFrame,
                  model_path:list[str]):
    num_models = len(model_path)
    next_col_idx=num_models
    new_node_id = node_df['node_id'].max()+1
    new_node_name = "extra_t0"
    new_node = pd.DataFrame(
            {
                "topic_id":new_node_name,
                "node_id":new_node_id,
                "label":"",
                "path_idx":next_col_idx,
                "model_id":"extra",
                "topic_num":0,
                "show_node": False
            },
            index =[0]
        )
    node_src,node_src_id = node_df.loc[(node_df['path_idx']==num_models-1),['topic_id','node_id']].values[0]
    new_link = pd.DataFrame({
            "source":node_src,
            "source_id":node_src_id,
            "target":new_node_name,
            "target_id":new_node_id,
            "value":1,
            "show_link":False
        },index=[0]
        )
    node_df = pd.concat([node_df,new_node]).reset_index(drop=True)
    link_df = pd.concat([link_df,new_link]).reset_index(drop=True)

    return node_df,link_df

def add_invis_source_node(
    needs_source,
    node_df,
    link_df,
    model_path
    ):
    data_list = needs_source.groupby('path_idx')[["topic_id",'node_id']].agg(list)
    for path_idx, floating_node_names, floating_node_ids in data_list.itertuples():
        prev_model = model_path[path_idx-1]
        new_node_id = node_df['node_id'].max()+1
        new_node_name = f"{prev_model}_t0"
        new_nodes = pd.DataFrame(
            {
                "topic_id":new_node_name,
                "node_id":new_node_id,
                "label":"",
                "path_idx":path_idx-1,
                "model_id":prev_model,
                "topic_num":0,
                "show_node": False
            },
            index =[0]
        )
        new_links = pd.DataFrame({
            "source":new_node_name,
            "source_id":new_node_id,
            "target":floating_node_names,
            "target_id":floating_node_ids,
            "value":1,
            "show_link":False
        },
        index=range(len(floating_node_names))
        )

        node_df = pd.concat([node_df,new_nodes]).reset_index(drop=True)
        link_df = pd.concat([link_df,new_links]).reset_index(drop=True)
        node_df['is_source'] = node_df['node_id'].isin(link_df['source_id'])
        node_df['is_target'] = node_df['node_id'].isin(link_df['target_id'])
    return node_df,link_df

def prep_data(data:dict,
              model_path:List[str],
              extra_col:bool=True,
              palette:Optional[List[str]]=None
              ):
    


    links = data['data']['links']
    nodes = data['data']['nodes']
    link_df = pd.DataFrame(links)
    node_df = pd.DataFrame(nodes)
    #node_df['label_wrapped'] = node_df['label'].apply(wrap_label)
    node_df['path_idx'] = node_df['model_id'].apply(model_path.index)
    link_df['show_link'] = True
    node_df['show_node'] = True
    node_df['is_source'] = node_df['node_id'].isin(link_df['source_id'])
    node_df['is_target'] = node_df['node_id'].isin(link_df['target_id'])
    
    if extra_col:
        node_df,link_df = add_extra_col(node_df,link_df,model_path)

    needs_source:pd.DataFrame = node_df[(node_df['path_idx']>0)&(node_df['is_target']==False)] #type:ignore
    while not needs_source.empty:
        node_df,link_df = add_invis_source_node(needs_source,node_df,link_df,model_path)
        needs_source:pd.DataFrame = node_df[(node_df['path_idx']>0)&(~node_df['is_target'])] #type:ignore

    node_df['label_wrapped'] = [wrap_label(l) if l!="" else "" for l in node_df['label'].values]

    node_df,link_df = add_color(node_df,link_df,palette)
    return node_df,link_df

# def plot_and_save(node_df,link_df,save_path):
#     pass



def add_color(node_df:pd.DataFrame,
              link_df:pd.DataFrame,
              palette:Optional[list[str]] = None
              ):
    _palette = palette or qc.Alphabet_r

    def get_color(row):
        if row['show_node']:
            n = row['node_id']
            return _palette[(n+1)%len(_palette)] #type:ignore
        return 'rgba(0,0,0,0)'
    
    node_df["color"] = node_df.apply(get_color,axis=1)
    color_dict = node_df.set_index('node_id')['color'].to_dict()
    link_df['source_color']=link_df['source_id'].apply(lambda x: color_dict.get(x))
    link_df['target_color']=link_df['target_id'].apply(lambda x: color_dict.get(x))
    
    return node_df,link_df

def make_plot_params_dicts(
    node_df:pd.DataFrame,
    link_df:pd.DataFrame,
    source_idx_col='source_id',
    target_idx_col='target_id',
    node_id_col='node_id',
    value_col='value',
    label_col:str='label_wrapped',
    node_color_col='color',
    link_color_col='target_color',
    node_opacity:float=0.8,
    link_opacity:float=0.4
    )->tuple[dict,dict]:

    node_df = node_df.copy().sort_values(node_id_col)
    link_df = link_df.copy()
    



    node_df['color']=node_df[node_color_col].apply(lambda x: hex_to_rgba(x,node_opacity))
    node_df.loc[~node_df['show_node'],"color"] = "rgba(0,0,0,0)"


    link_df['color']=link_df[link_color_col].apply(lambda x: hex_to_rgba(x,link_opacity))
    link_df.loc[~link_df['show_link'],"color"] = "rgba(0,0,0,0)"
    
    node_params = {
        "label":node_df[label_col].to_list(),
        "color":node_df['color'].to_list()
    }

    link_params={
        'source':link_df[source_idx_col].to_list(),
        'target':link_df[target_idx_col].to_list(),
        'value':link_df[value_col].to_list(),
        'color':link_df['color'].to_list()
    }
    return node_params,link_params


def main():

    json_paths = [f for f in os.listdir(JSON_DATA_PATH) if f.endswith(".json")]
    uncolored_dir = "results/sankeys/uncolored_plots"
    for j in json_paths:

        full_path = os.path.join(JSON_DATA_PATH,j)
        flow_id = j[:-5]
        with open(full_path, 'r') as f:
            data = json.load(f)
        model_path = data['model_ids']
        num_models = len(model_path)
        
        extra_col=(num_models>2)
        num_cols = num_models+int(extra_col)
        node_df,link_df = prep_data(data,model_path,extra_col)

        node_params,link_params = make_plot_params_dicts(
            node_df,
            link_df,
            node_opacity=0.95,
            link_opacity=0.4
        )

        node_params.update({
            'align' : 'left',
            'line': {'width': 0}
            })
        top_titles = [get_model_title(t) for t in model_path] +([""] if extra_col else [])
        
        three_line_title_pad = 20*int(any([t.count("<br>")>1 for t in top_titles]))
        fig_width = (350*num_cols-700 if extra_col else 600)


        save_path = os.path.join(uncolored_dir,flow_id+".png")
        title_params=dict(
            title_format = lambda x: f"<b>{x}"
        )
        save_params=dict(
            scale=2
        )
        fig_layout_params = dict(
            margin=dict(t=60+three_line_title_pad,b=50-three_line_title_pad,l=40,r=20)
        )
        make_save_sankey(
            node_params,
            link_params,
            fig_height=1200,
            fig_width=fig_width,
            sankey_column_labels=top_titles,
            title_params=title_params,
            fig_layout_params=fig_layout_params,
            image_save_path = save_path,
            show_plot=False,
            save_params=save_params
        )

        # make_save_sankey(
        #     source_ids:node_df['source_id'],
        #     target_ids:list[int],
        #     values:list[float],
        #     labels:list[str],
        #     fig_height = 600,
        #     fig_width = 1000,
        #     sankey_column_labels: Optional[list[str]] = None,
        #     title_params: Optional[dict] = None,
        #     show_plot = True,
        #     image_save_path:Optional[str] = None,
        #     addl_node_params:Optional[dict] = None,
        #     addl_link_params:Optional[dict] = None,
        #     fig_layout_params:Optional[dict] = None,
        #     save_params:Optional[dict[str,Any]] = None
        #     )
        
        # end open file
    




if __name__ == "__main__":
    main()
# end main



