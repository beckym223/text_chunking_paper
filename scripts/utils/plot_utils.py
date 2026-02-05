import pandas as pd
import re
from plotly import graph_objects as go
import os
import json
from typing import List, Dict, Tuple,Any, Optional,Callable

def basic_sankey_fig(
    links_dict,
    nodes_dict,
    height:int=950,
    width=500,
    **layout_kwargs
    ):


    chart1 = go.Sankey(link=links_dict, node=nodes_dict,
    arrangement='snap'
                       #arrangement="snap"
                    )
    fig = go.Figure(chart1)
    fig.update_layout(
        height=height,
        width=width,
        **layout_kwargs
                    )
    return fig

def add_titles(
    fig:go.Figure,
    title_list:list[str|None],
    title_y=1,
    title_format:Optional[Callable[[str],str]] = None,
    title_font_size = 20,
    **title_kwargs):

    title_format = title_format if title_format is not None else lambda s:s
    title_kwargs = title_kwargs or {}
    font_args:dict[str,Any] = {**title_kwargs.pop('font',{}),'size':title_font_size}
    
    n_col = len(title_list)

    left_title = title_list[0]
    right_title = title_list[-1] if ncol>1 else None
    center_titles = [(title_list[x],x/(n_col-1)) for x in range(1,n_col-1)]
    
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
    
    return fig


def save_fig(
    fig,
    path,
    exist_ok=True,
    make_dirs=True,
    **save_params
    )

    if not exist_ok and os.path.exists(path):
        raise FileExistsError(f"{path} exists")
    if make_dirs:
        os.make_dirs(os.path.dirname(path),exist_ok=True)

    fig.write_image(path,**save_params)
    

def make_save_sankey(
    source_ids:list[int],
    target_ids:list[int],
    values:list[float],
    labels:list[str],
    fig_height = 600,
    fig_width = 1000,
    sankey_column_labels: Optional[list[str]] = None,
    title_params: Optional[dict,str] = None,
    show_plot = True,
    image_save_path:Optional[str] = None,
    addl_node_params:Optional[dict] = None,
    addl_link_params:Optional[dict] = None,
    fig_layout_params:Optional[dict] = None,
    save_params:Optional[dict] = None
    ):

    node_params = addl_node_params or {}
    link_params = addl_link_params or {}

    node_dict = {
        **node_params,
        "labels":labels
    }

    link_dict = {
        "source":source_ids,
        "target":target_ids,
        "values":values,
        **link_params
    }

    fig = basic_sankey_fig(
        node_dict,
        link_dict,
        height=fig_height,
        width = fig_width,
        **layout_kwargs
    )

    if sankey_column_labels is not None:
        add_titles(
            fig,
            sankey_column_labels,
            **title_params
        )

    if show_plot:
        fig.show()
    if image_save_path is not None:
        save_fig(
            fig,
            image_save_path,
            **save_params
            )

def plot_sankey(links_dict:Dict[str,list],
                nodes_dict:Dict[str,list],
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