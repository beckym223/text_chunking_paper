# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: notebooks//ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
# ---

# %%
import pandas as pd
import re
from plotly import graph_objects as go
import os
import json
from typing import List, Dict, Tuple,Any, Optional,Callable
os.chdir("/home/marcu22r_mtholyoke_edu/cleaner_package")
#test 3
# %%
os.path.dirname

# %%
chunk_display_names=dict(
        document  = "full document",
        page      = "page",
        paragraph = "paragraph",
        sent_200  = "200 word: nearest sentence",
        sent_500  = "500 word: nearest sentence",
        word_200 = "200 word",
        word_500 = "500 word",
        word_500_ol = "500 word overlapping"
    )

chunk_abrev=dict(
    document  = "doc",
    page      = "pg",
    paragraph = "par",
    sent_200  = "sen2",
    sent_500  = "sen5",
    word_200 = "w2",
    word_500 = "w5",
    word_500_ol = "w5ol"
)

from plotly.colors import qualitative as qc
import itertools as it

COLOR_NO_LIST = ['#FE00CE',
           '#E3EE9E',
           "#E48F72",
           '#C9FBE5',
           '#F7E1A0',
           "#DC587D",
           "#FBE426",
           "#F6222E",
           #"#6A76FC"
           #'#1C8356',
           "#1CBE4F",
            "#D626FF",
           "#AA0DFE",
           '#1CFFCE',
           '#00FE35',
           "#479B55",
           "#EEA6FB",
           "#FF9616",
           "#2ED9FF",
           "#FA0087",
           "#FE00CE",
           "#F6223E",
           "#90AD1C",
           "#FED4C4",
           '#E2E2E2',]   
PALETTE = [p for p in qc.Light24+qc.Alphabet_r if p not in COLOR_NO_LIST]#type:ignore

def get_color(n):
    try:
        return PALETTE[(n+1)%len(PALETTE)]
    except IndexError:
        print(n)
        print(len(PALETTE))
        raise


# %%
link_df= pd.read_csv("results/sankeys/doc_10k_pg_10k_w5_18k/link_df.csv")

node_df = pd.read_csv("results/sankeys/doc_10k_pg_10k_w5_18k/node_df.csv")


# %%
link_df

# %%
re.match(r"([\w\d]+?)_(\d+)k",model_id).groups()

# %%

def wrap_label(label,n_to_wrap=3):
    pattern = r"((?:\w+(?:,|:)\s?){%d})\s" % n_to_wrap
    return "<b>"+re.sub(pattern,"\\1<br>",label)

def get_model_title(model_id:str)->str:
    chunk_name,k = re.match(r"([\w\d]+?)_(\d+)k",model_id).groups(default=('err',-1))
    return f"<b>{chunk_display_names.get(chunk_name,"NA").title()}<br>K={k}"

def get_x_positions(idxs:list[int],min_x:float=0,max_x:float=1):
    max_num = max(idxs)
    num_cols = max_num+1+int(max_num>1)
    x_range = max_x-min_x
    return [min_x+n*x_range/num_cols for n in idxs]


# %%
def plot_sankey(links_dict,
                nodes_dict,
                height:int=950,
                width=500,
                title_size=20,
                two_col=False,
                title_y=1,
                left_title: Optional[str] =None,
                right_title:Optional[str] =None,
                other_titles:Optional[list[tuple[str,float]]] =None,
                title_kwargs:Optional[dict[str,Any]] = None,
                plot=True,
                title_format:Optional[Callable[[str],str]] = None
                ):
                
    title_format = title_format if title_format is not None else lambda s:s
    title_kwargs = title_kwargs or {}
    font_args:dict[str,Any] = {**title_kwargs.pop('font',{}),'size':title_size}
    center_titles = other_titles if other_titles is not None else []
    
    titles = [left_title,right_title,*[x[0] for x in center_titles]]
    #print(f"Column titles: {titles}")
    
    #exclude_titles = [x.lower() for x in exclude_titles] if exclude_titles is not None else []
    chart1 = go.Sankey(link=links_dict, node=nodes_dict,
    arrangement='snap'
                       #arrangement="snap"
                    )
    fig = go.Figure(chart1)
    fig.update_layout(height=height,width=width,
                    margin=dict(t=50,b=50,l=20,r=20)
                    )
    if left_title is not None:
        fig.add_annotation(
            text=title_format(left_title),
            y=title_y,
            x=0,
            xanchor='left',
            yanchor='bottom',
            font=font_args,
            showarrow=False,
            **title_kwargs
            )
    if right_title is not None:
        fig.add_annotation(
            text=title_format(right_title),
            y=title_y,
            x=1,
            xanchor='right',# if two_col else 'center',
            yanchor='bottom',
            font=font_args,
            showarrow=False,
            **title_kwargs
            )
    for text,x in center_titles:
        #print(text,x)
        fig.add_annotation(
                text=title_format(text),
                y=title_y,
                font=font_args,
                x=x,
                xanchor='center',
                yanchor='bottom',
                showarrow=False,
                **title_kwargs
                )
    
    if plot:
        fig.show()
    return fig

# %%
class SankeyData(dict):

    def __init__(self, data):
        """
        Purpose: value
        """
        self.data=data

    # end alternate constructor

    def __getattr__(self, attribute):
        return self.data.get(attribute)
d = SankeyData(data)

# %%
from dataclasses import dataclass
help(dataclass)

# %%
l = d.links
l.keys()

# %%
data = json.load(open("results/sankeys/json_data/doc_10k_pg_10k_sen5_11k_par_11k.json"))


# %%
data = json.load(open("results/sankeys/json_data/doc_10k_pg_10k_sen5_11k_par_11k.json"))
out_dict = {}
model_path = data["model_ids"]
top_titles = [get_model_title(t) for t in model_path]
# if len(top_titles)>2:
#     top_titles+=['']
links = data['data']['links']
nodes = data['data']['nodes']
links.keys()

# %%
links = data['data']['links']
nodes = data['data']['nodes']
link_df = pd.DataFrame(links)
node_df = pd.DataFrame(nodes)
#node_df['label_wrapped'] = node_df['label'].apply(wrap_label)
node_df['path_idx'] = node_df['model_id'].apply(model_path.index)
link_df['show_link'] = True
node_df['show_node'] = True

needs_source = node_df[(node_df['path_idx']>0)&(~node_df['is.target'])]
while not needs_source.empty:
    for idx, row in needs_source: #
        pass
    break
        

needs_source = node_df[(node_df['path_idx']>0)&(~node_df['is.target'])]
needs_source


# %%
li = needs_source.groupby(['model_id','path_idx'])[["topic_id",'node_id']].agg(list)
for (a,b), c, d, in li.itertuples():
    print(a,b,c,d)

# %%

for (model_id,path_idx), floating_node_names, floating_node_ids in needs_source.groupby(['model_id','path_idx'])[["topic_id",'node_id']].agg(list).itertuples():
    prev_model = model_path[path_idx-1]
    new_node_id = node_df['node_id'].max()+1
    new_node_name = f"{prev_model}_t0"
    new_nodes = pd.DataFrame(
        {
            "topic_id":new_node_name,
            "node_id":new_node_id,
            "is.target":False,
            "is.source":True,
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
        "overlap_size":1,
        "show_link":True
    },
    index=range(len(floating_node_names))
    )
    
    

    



# %%
node_df[(node_df['path_idx']>0)&(~node_df['is.target'])].empty

# %%
new_links

# %%
link_df.columns

# %%
# def add_invis_node_link(link_df,node_df,model_path:list[str],node_row:pd.Series):
#     #prev_name = 
#     new_node_id = node_df['node_id'].max()+1
#     #new_node_name= 
#     new_node_path_idx = node_row.path_idx-1
#     new_node_target = node_row.node_id
#     invis_model = model_path[new_node_path_idx]

#     new_node_row = dict(
#         node_id = new_node_id,
#         path_idx = new_path_idx
#     )
#     new_link_row = dict(
#         #source = 

#     )

    # for i in range(num_needed):
    #     node_row = pd.Series(
    #         dict(
    #             topic_id = f"invis{new_node_id}",
    #             model_id = model_id"
                
    #         )
                
    #             top
    #         }
    #     )




add_invis_node_link(link_df,node_df,needs_source.iloc[0])

# %%
data = json.load(open("results/sankeys/json_data/doc_10k_pg_10k_sen5_11k_par_11k.json"))
out_dict = {}
model_path = data["model_ids"]
top_titles = [get_model_title(t) for t in model_path]
# if len(top_titles)>2:
#     top_titles+=['']
links = data['data']['links']
nodes = data['data']['nodes']
nodes['path_idx'] = [model_path.index(m) for m in nodes['model_id']]
nodes['label_wrapped'] = [wrap_label(l) for l in nodes['label']]
num_cols = len(top_titles)
add_extra = num_cols>2
fig_width = 350*num_cols-300
left_title = top_titles[0]
right_title = top_titles[-1]
center_titles = [] if num_cols<=2 else [(top_titles[x],x/(num_cols-1)) for x in range(1,num_cols-1)]



links_out = dict(
    source = links['source_id'],
    target = links['target_id'],
    value = links['overlap_size']
)

nodes_out = {
        'label': nodes['label_wrapped'],
        "x" : get_x_positions(nodes['path_idx']),
        'align' : 'left',
        #'color':node_colors,
        #'custom_data': node_colors,
        #'hovertemplate':' %{label}<br>Color: %{color}<extra></extra>', 
        'line': {'width': 0}
    }

f = plot_sankey(
    links_out,
    nodes_out,
    width = fig_width,
    two_col = num_cols==2,
    left_title=left_title,
    right_title=right_title,
    other_titles = center_titles,
    title_format = lambda t: f"<b>{t}"

)

# %%


# %%


# %%


# %%
link_dict.keys()

# %%
color_link

# %%


def hex_to_rgba(hex_color, alpha=0.85):
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'rgba({r},{g},{b},{alpha})'
    else:
        return 'rgba(0,0,0,0)'  # fallback
top_titles = [get_model_title(t) for t in model_path]
# if len(top_titles)>2:
#     top_titles+=['']
links = data['data']['links']
nodes = data['data']['nodes']
nodes['path_idx'] = [model_path.index(m) for m in nodes['model_id']]
nodes['label_wrapped'] = [wrap_label(l) for l in nodes['label']]
num_cols = len(top_titles)
add_extra = num_cols>2
fig_width = 350*num_cols-200
left_title = top_titles[0]
right_title = top_titles[-1]
center_titles = [] if num_cols<=2 else [(top_titles[x],x/(num_cols-1)) for x in range(1,num_cols-1)]


combos = [
    (4,9,2,10),
    (2,2,9,4),
    (8,5,10,2),
    (6,8,5,8),
    (9,7,1,3),
    (-1,-1,11,11),
    (-1,-1,6,7),
    ([1,10],4,4,[4,9])

]


link_df = pd.DataFrame(links)
node_df = pd.DataFrame(nodes)[['topic_id','model_id','topic_num','is.source','is.target','node_id','path_idx','label_wrapped']]
color_node,color_link = color_nodes_by_combos(
    link_df,
    node_df,
    combos,
    model_path
)
node_dict = color_node.to_dict(orient='list')
link_dict = color_link.to_dict(orient = 'list')
link_opacity=0.35
link_color_alpha = [hex_to_rgba(l,link_opacity) for l in link_dict['link_color']]
color_links_out = dict(
    source = link_dict['source_id'],
    target = link_dict['target_id'],
    value = link_dict['overlap_size'],
    color=link_color_alpha
)

nodes_out = {
        'label': node_dict['label_wrapped'],
        "x" : get_x_positions(node_dict['path_idx']),
        'align' : 'left',
        'color': node_dict['node_color'],
        #'custom_data': node_colors,
        #'hovertemplate':' %{label}<br>Color: %{color}<extra></extra>', 
        'line': {'width': 0}
    }
f = plot_sankey(
    color_links_out,
    nodes_out,
    width = fig_width,
    two_col = num_cols==2,
    left_title=left_title,
    right_title=right_title,
    other_titles = center_titles,
    title_format = lambda t: f"<b>{t}"

)

#f.write_image("results/sankeys/colored_path_test.png",scale=2)


# %%


# %%
hex_to_rgba(link_dict['link_color'][1])

# %%
def color_nodes_by_combos(
    link_df,
    node_df,
    combos: list[tuple],
    model_id_list:list[str],
    cust_palette=None,
    palette_start_idx=0,
    color_mapping:dict|None = None):

    color_dict = color_mapping or {}
    palette =  cust_palette or PALETTE

    allowed_paths = list(it.pairwise(model_id_list))
    palette=PALETTE
    palette_start_idx=0
    combo_df = pd.DataFrame(combos,columns=model_id_list)
    combo_df['prioritized'] =True
    num_topics = node_df.groupby('model_id')['topic_num'].max()[model_id_list]
    to_concat = []
    
    ### Add "combos" of single topics to have unique colors
    for g in model_id_list:
        max_t= num_topics[g]
        temp = pd.DataFrame({
            g:[
                *set(range(1,max_t+1)).difference(
            combo_df[combo_df[g].apply(lambda x: isinstance(x,int))][g])]})
        to_concat.append(temp)
    combo_df=pd.concat([combo_df,*to_concat]).fillna(-1).reset_index(drop=True)
    

    #set priority based on ordering
    combo_df['priority'] = combo_df.index

    #get color from palette
    combo_df['temp_color'] = ((palette[palette_start_idx:]+palette[:palette_start_idx])*2)[:len(combo_df)]

    # start with custom mapping, then fill in from palette
    color_map_list = list([*k,v] for k,v in color_dict.items())
    start_flow =pd.DataFrame(data=color_map_list,columns = model_id_list +['flow_color'])
    combo_colored = combo_df.merge(start_flow,
                    #left_on=flow_groups,
                    #right_on = flow_groups,
                    how='left')
    combo_colored['flow_color']=combo_colored['flow_color'].fillna(combo_colored.pop('temp_color'))


    # expand lists in combos
    for m in model_id_list:
        combo_colored = combo_colored.explode(m)
    
    #verify data type
    combo_colored[model_id_list] = combo_colored[model_id_list].map(int)

    #make any with -1 be not a priority
    combo_colored['prioritized'] = combo_colored['prioritized']!=-1

    # Make dataframe of links and colors
    # link_color_priority_df = pd.concat([
    # pd.DataFrame({
    #     "source":s+"_t"+combo_colored[s].astype(int).astype(str),
    #     'target':t+"_t"+combo_colored[s].astype(int).astype(str),
    #     'priority':combo_colored['priority'],
    #     'prioritized':combo_colored['prioritized'],
    #     'flow_color':combo_colored['flow_color']
    # }) for s,t in allowed_paths])

    # melt to color nodes
    colored_model_topic_num = combo_colored.melt(id_vars = ['flow_color','priority','prioritized'],value_name="topic_num",var_name='model_id')
    color_node_df = node_df.merge(colored_model_topic_num,how='left').drop_duplicates('topic_id')
    
    # merge with source and targets of links
    merge_cols = ['topic_id','node_id','flow_color','priority','prioritized']
    source_merge_cols = ['source','source_id','source_flow_color','source_priority',"source_prioritized"]
    target_merge_cols = ['target','target_id','target_flow_color','target_priority','target_prioritized']
    link_named_source = color_node_df[merge_cols].set_axis(source_merge_cols,axis=1)
    source_merged = link_df[['source','target','overlap_size']].drop_duplicates().merge(link_named_source,on=['source'])

    link_named_target = color_node_df[merge_cols].set_axis(['target','target_id','target_flow_color','target_priority','target_prioritized'],axis=1)
    source_target_merged = source_merged.merge(link_named_target,on=['target'])
    link_color_df= source_target_merged#.merge(flow_df,on=['source','target'],how='left')
    
    ### Logic for link color prioritization

    # Option for only making given combos be colored
    link_color_df['defined_flow'] = link_color_df['source_flow_color'] == link_color_df['target_flow_color']
    link_color_df.loc[link_color_df['defined_flow'],'defined_color'] = link_color_df.loc[link_color_df['defined_flow'],"source_flow_color"]
    link_color_df['only_defined'] = link_color_df['defined_color'].fillna('#808080')

    link_color_df['link_color'] = link_color_df.apply(lambda row:
                                                row['only_defined'] if row['defined_flow']
                                                else (row['target_flow_color'] if row['target_priority']<row['source_priority']
                                                        else row['source_flow_color']),axis=1).fillna('#808080')

    link_df = link_color_df[['source','target','overlap_size','source_id','target_id','link_color']]
    node_df = color_node_df.drop(['priority','prioritized'],axis=1).rename(columns={'flow_color':'node_color'})
    return node_df, link_df
    #link_color_df[['source_color_exists','target_color_exists']] = ~link_color_df[['source_flow_color','target_flow_color']].isna()


# %%
def make_sankey_params_invisible_nodes(
    link_df:pd.DataFrame,
    node_df:pd.DataFrame,
    source_idx_col='source_id',
    target_idx_col='target_id',
    value_col='value',
    #filter_col = 'show_color',
    display_col='label_wrapped',
    node_color_col='color',
    link_color_col='target_color',
    #invis_nodes=True,
    link_opacity=0.4,
    scale_opacity=False,
    opacity_step_val=0.05,
) -> tuple[dict[str,str|list],dict[str,str|list]]:
    # exclude_mask_lab = label_df[filter_col].to_list()
    # exclude_mask_link = val_df[filter_col].to_list()


    source_idx = val_df[source_idx_col].tolist()
    target_idx = val_df[target_idx_col].tolist()
    values = val_df[value_col].to_list()
    

    #node_colors = get_color_array(label_df, color_col, exclude=col_exclude, palette=cust_palette)
    label_df = label_df.copy().sort_index()

    node_colors_temp = label_df[node_color_col].to_list()
    node_colors:list[str] = [nc if inc else 'rgba(0,0,0,0)' for nc, inc in zip(node_colors_temp,exclude_mask_lab)] if invis_nodes else node_colors_temp
    nodes_dict = {
        'label': label_df[display_col].tolist(),
        'color':node_colors,
        #'custom_data': node_colors,
        'hovertemplate':' %{label}<br>Color: %{color}<extra></extra>', 
        'line': {'width': 0}
    }

    # Default invisible/gray link fallback
    default_link_colors = [
        'rgba(0,0,0,0)' if x else f'rgba(64,64,64,{(link_opacity+opacity_step_val*y if scale_opacity else link_opacity)})'
        for x, y in zip(
            val_df[['source', 'target']].apply(lambda x: x.str.startswith('_')).any(axis=1).tolist(),
            val_df[value_col].to_list()
        )
    ]

    link_colors = default_link_colors  # fallback
    
    if link_color_col and link_color_col in val_df.columns:
        if scale_opacity:
            link_colors = val_df.apply(lambda row: hex_to_rgba(row[link_color_col],alpha = link_opacity+row['value']*opacity_step_val),axis=1)

        else:
            link_colors = val_df[link_color_col].apply(lambda x: hex_to_rgba(x,alpha=link_opacity))


    links_dict = {
        'source': source_idx,
        'target': target_idx,
        'value': values,
        'color': [lc if inc else 'rgba(0,0,0,0)' for lc, inc in zip(link_colors,exclude_mask_link)]
    }

    return nodes_dict, links_dict

# %% [markdown]
# # Break

# %%
comb['priority'] = comb.index
comb['temp_color'] = ((palette[palette_start_idx:]+palette[:palette_start_idx])*2)[:len(comb)]

start_flow =pd.DataFrame(data=flow_list,columns = list(model_path) +['flow_color'])#,
                                #columns = [*flow_groups,'flow_color'])
comb = comb.merge(start_flow,
                    #left_on=flow_groups,
                    #right_on = flow_groups,
                    how='left')

comb['flow_color']=comb['flow_color'].fillna(comb.pop('temp_color'))
#comb['flow_color'] = comb['flow_color'].fillna(fill_colors[:len(comb)])
for g in model_path:
        comb = comb.explode(g)
comb[model_path] = comb[model_path].map(int)
comb['prioritized'] = comb['prioritized']!=-1

# %%
flow_df = pd.concat([
    pd.DataFrame({
        "source":s+"_t"+comb[s].astype(int).astype(str),
        'target':t+"_t"+comb[s].astype(int).astype(str),
        'priority':comb['priority'],
        'prioritized':comb['prioritized'],
        'flow_color':comb['flow_color']
    }) for s,t in allowed_paths])


# %%
colored_model_topic_num = comb.melt(id_vars = ['flow_color','priority','prioritized'],value_name="topic_num",var_name='model_id')
color_node_df = node_df.merge(colored_model_topic_num,how='left').drop_duplicates('topic_id')
merge_cols = ['topic_id','node_id','flow_color','priority','prioritized']
temp_label = node_merged_color[merge_cols].set_axis(['source','source_id','source_flow_color','source_priority',"source_prioritized"],axis=1)
source_merged = link_df[['source','target','overlap_size']].drop_duplicates().merge(temp_label,on=['source'])
source_target_merged = source_merged.merge(node_merged_color[merge_cols].set_axis(['target','target_id','target_flow_color','target_priority','target_prioritized'],axis=1),on=['target'])
color_merged = source_target_merged.merge(flow_df,on=['source','target'],how='left')


# %%
color_merged[['source_color_exists','target_color_exists']] = ~color_merged[['source_flow_color','target_flow_color']].isna()
def logic(row):
    if row['target_prioritized'] and not row['source_prioritized']:
        return row['source_flow_color']
    if not row['target_prioritized'] and row['source_prioritized']:
        return row['target_flow_color']
    if row['source_prioritized'] and row['target_prioritized']:
        return 
    return row['defined_color']
def compare_prior(row):
    if not row['defined_row'] and row['source_prioritized'] and row['target_prioritized']:
        return row['source_flow_color'] if row['source_priority']>row['target_priority'] else row['target_flow_color']
    return row['defined_color']
#color_merged[['source_priority','target_priority']] = color_merged[['source_priority','target_priority']].fillna(len(color_merged))
max_priority = color_merged['priority'].max()
color_merged[['source_color_exists','target_color_exists']] = ~color_merged[['source_flow_color','target_flow_color']].isna()
color_merged['defined_flow'] = color_merged['source_flow_color'] == color_merged['target_flow_color']
color_merged.loc[color_merged['defined_flow'],'defined_color'] = color_merged.loc[color_merged['defined_flow'],"source_flow_color"]
color_merged['only_defined'] = color_merged['defined_color'].fillna('#808080')
color_merged['conditional_flow'] = color_merged.apply(logic,axis=1).fillna('#808080')

color_merged.loc[(color_merged['conditional_flow']!='#808080')&(~color_merged['defined_flow']),'priority']=max_priority+1

color_merged['flow_color'] = color_merged.apply(lambda row:
                                                row['only_defined'] if row['defined_flow']
                                                else (row['target_flow_color'] if (row['target_color_exists'] and not row['source_color_exists'] or row['target_priority']<row['source_priority'])
                                                        else row['source_flow_color']),axis=1).fillna('#808080')

link_color_df = (color_merged.copy()
            .sort_values('priority')
            .drop_duplicates(['source','target','overlap_size'])
            )


# %%
color_merged

# %%
link_df
def color_by_combo(
    links,
    nodes,
    model_path,
    combos,
    palette,
    color_dict):
    pass
    # start_label,
    #                data,
    #                combos:list[tuple],
    #                flow_groups:list[str],
    #                flow_group_col = 'group',
    #                fill_unique=True,
    #                cust_palette=None,
    #                reverse_priority =False,
    #                palette_start_idx = 0,
    #                color_dict = None
    #                ):
    color_dict = color_dict or {}
    palette =  cust_palette or PALETTE
    allowed_paths = list(it.pairwise(model_path))
    to_concat = []
    comb = pd.DataFrame(combos,columns = flow_groups)
    comb['prioritized'] = True
    fill_unique=True
    if fill_unique:
        num_topics = start_label.groupby(flow_group_col)['num'].max()[flow_groups]
        for g in flow_groups:
            max_t = num_topics[g]
            temp = pd.DataFrame({
                g:[
                    *set(range(1,max_t+1)).difference(
                comb[comb[g].apply(lambda x: isinstance(x,int))][g])]})
            to_concat.append(temp)


    comb = pd.concat([comb,*to_concat]).fillna(-1).reset_index(drop=True)

    comb['priority'] = comb.index
    comb['temp_color'] = ((palette[palette_start_idx:]+palette[:palette_start_idx])*2)[:len(comb)]
    
    start_flow =pd.DataFrame(data=flow_list,columns = list(flow_groups) +['flow_color'])#,
                                   #columns = [*flow_groups,'flow_color'])
    comb = comb.merge(start_flow,
                      #left_on=flow_groups,
                      #right_on = flow_groups,
                      how='left')
    
    comb['flow_color']=comb['flow_color'].fillna(comb.pop('temp_color'))
    #comb['flow_color'] = comb['flow_color'].fillna(fill_colors[:len(comb)])
    for g in flow_groups:
            comb = comb.explode(g)
    comb[flow_groups] = comb[flow_groups].map(int)
    comb['prioritized'] = comb['prioritized'].fillna(False)
    flow_df = pd.concat([
        pd.DataFrame({
            "source":s+comb[s].astype(int).astype(str),
            'target':t+comb[t].astype(int).astype(str),
            'priority':comb['priority'],
            'prioritized':comb['prioritized'],
            'flow_color':comb['flow_color']
        }) for s,t in allowed_paths])

    combo = comb.melt(id_vars = ['flow_color','priority','prioritized'])
    make_id_col(combo,'id','variable','value')
    merged = start_label.merge(combo[['flow_color','id','priority','prioritized']],how='left')
    sankey_label_df =merged.sort_values('priority').drop_duplicates('id').sort_values('node_id')
    sankey_label_df['flow_color'] = sankey_label_df['flow_color'].fillna('#808080')
    max_priority = sankey_label_df['priority'].max()
    merge_cols = ['id','node_id','flow_color','priority','prioritized']
    temp_label = merged[merge_cols].set_axis(['source','source_id','source_flow_color','source_priority',"source_prioritized"],axis=1)
    assert temp_label['source_prioritized'].any(), "We weren't able to find the source prioritization"

    source_merged = data[['source','target','value']].drop_duplicates().merge(temp_label,on=['source'])
    source_target_merged= source_merged[source_merged['value']!=0].merge(merged[merge_cols].set_axis(['target','target_id','target_flow_color','target_priority','target_prioritized'],axis=1),on=['target'])

    source_target_merged['show_color'] = source_target_merged['target'].str.startswith("_")==False
    color_merged = source_target_merged.merge(flow_df,on=['source','target'],how='left')
    assert (color_merged['source_prioritized']^color_merged['target_prioritized']).any(), "Bestie still no prioritization"
    def logic(row):
        if row['target_prioritized'] and not row['source_prioritized']:
            return row['source_flow_color']
        if not row['target_prioritized'] and row['source_prioritized']:
            return row['target_flow_color']
        if row['source_prioritized'] and row['target_prioritized']:
            return 
        return row['defined_color']
    def compare_prior(row):
        if not row['defined_row'] and row['source_prioritized'] and row['target_prioritized']:
            return row['source_flow_color'] if row['source_priority']>row['target_priority'] else row['target_flow_color']
        return row['defined_color']
    #color_merged[['source_priority','target_priority']] = color_merged[['source_priority','target_priority']].fillna(len(color_merged))
    color_merged[['source_color_exists','target_color_exists']] = ~color_merged[['source_flow_color','target_flow_color']].isna()
    color_merged['defined_flow'] = color_merged['source_flow_color'] == color_merged['target_flow_color']
    color_merged.loc[color_merged['defined_flow'],'defined_color'] = color_merged.loc[color_merged['defined_flow'],"source_flow_color"]
    color_merged['only_defined'] = color_merged['defined_color'].fillna('#808080')
    color_merged['conditional_flow'] = color_merged.apply(logic,axis=1).fillna('#808080')
    
    color_merged.loc[(color_merged['conditional_flow']!='#808080')&(~color_merged['defined_flow']),'priority']=max_priority+1


    color_merged['flow_color'] = color_merged.apply(lambda row:
                                                    row['only_defined'] if row['defined_flow']
                                                    else (row['target_flow_color'] if (row['target_color_exists'] and not row['source_color_exists'] or row['target_priority']<row['source_priority'])
                                                          else row['source_flow_color']),axis=1).fillna('#808080')
                                                          

                                                    
                                                    #['flow_color']#.fillna(color_merged.apply(lambda row: row['target_flow_color'] if
                                                                                    # (row['target_color_exists'] and not row['source_color_exists'])
                                                                                    #  #and not row['source_color_exists']) or row['target_priority']<=row['source_priority']
                                                                                    # else row['source_flow_color'],axis=1))
                                                                                #if (pd.isna(row['source_priority']) and not pd.isna(row['target_priority'])) or row['target_priority']<row['source_priority']) else row['source_flow_color']
    #print(color_merged[['source','target','value']].value_counts().head())                  
    using = (color_merged.copy()[color_merged['value']!=0]
            .sort_values('priority')
            .drop_duplicates(['source','target','value'])
            )
    return using, sankey_label_df

# %%

color_merged[~color_merged['target_color_exists']]

# %%
node_df

# %%
fig = go.Figure(
    data=go.Sankey(
        node=dict(label=node_df['label_wrapped']),
        link = dict(
            source=link_df['source_id'],
            target=link_df['target_id'],
            value=link_df['overlap_size']
            
        )
    )
)
fig.update_layout(height=1000,width=1000,
                    margin=dict(t=50,b=50,l=20,r=20)
                    )
fig.show()

# %%



