import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
import plotly.express as px
import numpy as np
import dash_table
from skimage import io
from skimage.transform import resize, rotate
import pandas as pd
import os
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from dash.dependencies import Input,Output, State, MATCH
import plotly.graph_objects as go
import graph_computation



#external layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#init
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
loc_info = pd.read_csv('dbs/special_nodes.csv')
graph = pd.read_csv("dbs/nodes.csv", index_col=None)
directions = graph.set_index(['From','To']).to_dict()['direction']
name_vs_node = loc_info.dropna().set_index('Name').to_dict()['Node']
print(name_vs_node)
#configuring logo
encoded_klinik_logo = base64.b64encode(open('logos/klinik.png','rb').read())

app.layout = html.Div([
	#title and logo
	html.Div([
		html.Div([
				html.Div([
                html.Img(src='data:image/png;base64,{}'.format(encoded_klinik_logo.decode()), style={'width':'350','height':'68px', 'float':'left'}),
                html.H1(children='Westpfalz Klinikum WayFinder',style={ 'fontSize': 24, 'text-align':'center','padding-right':'60px','padding-top':'40px'})
                ])
			], className='row'
		),
		html.Div([
			html.H2(children='From', style={'fontSize': 24, 'padding-left':'40px', 'float':'left'}),
			html.H2(children='To',style={ 'fontSize': 24,'padding-right':'80px', 'float':'right'})
		],
		className='row', style={'padding-top':'40px'}),
		html.Div([
		html.Div(
		dcc.Dropdown(id='from',
			        options=[
			            {'label': 'ToiletI', 'value': 'ToiletI'},
						{'label': 'ToiletII', 'value': 'ToiletII'},
					  {'label': 'Entrance', 'value': 'Entrance'},
					  {'label': 'X-ray room', 'value': 'X-ray room'},
					  {'label': 'Cafeteria', 'value': 'Cafeteria'}
			        ]
    		), className = 'pretty_container four columns', style={'padding-left':'40px'}),
		html.Div(
			dcc.Dropdown(id='to',
			        options=[
			              {'label': 'ToiletI', 'value': 'ToiletI'},
						  {'label': 'ToiletII', 'value': 'ToiletII'},
  			            {'label': 'Entrance', 'value': 'Entrance'},
  			            {'label': 'X-ray room', 'value': 'X-ray room'},
  						{'label': 'Cafeteria', 'value': 'Cafeteria'}
			        ]
    		),className = 'pretty_container four columns', style={'width':'350','height':'68px', 'float':'right', 'padding-right':'40px'})
		], style={ 'padding-top':'20px'}, className = 'row')
    ]),
	#Testing directions
	#full slides
	html.Div([
		html.Div(html.A(["☜"], id='prev_loc', style={'text-decoration':'None','font-size': '78px', 'vertical-align': 'middle'}), style={'float':'left'}),
		html.Div(html.A(["☞"], id='next_loc', style={'text-decoration':'None','font-size': '78px', 'vertical-align': 'middle'}), style={'float':'right'}),
		html.Div(id='loc_img')
	],className='row')
])

def get_shortest_path(_from, to):
	return graph_computation.dijkstra(str(_from), str(to), graph)


curr_loc = 0
prev_loc = 11
next_loc = 1
prev_to = 'ToiletI'
prev_from = 'ToiletII'
prev_path = ['1','2','5','9']
@app.callback(
    dash.dependencies.Output('loc_img', 'children'),
    [dash.dependencies.Input('prev_loc', 'n_clicks'),
	dash.dependencies.Input('next_loc', 'n_clicks'),
	dash.dependencies.Input('to', 'value'),
	dash.dependencies.Input('from', 'value')])
def update_output(new_prev_loc, new_next_loc, new_to, new_from):
	global prev_loc, next_loc, curr_loc, prev_to, prev_from, prev_path
	#if prev or next was changed
	if prev_loc != new_prev_loc:
		prev_loc = new_prev_loc
		curr_loc -= 1
		curr_loc %= len(prev_path)
	elif next_loc != new_next_loc:
		next_loc = new_next_loc
		curr_loc += 1
		curr_loc %= len(prev_path)
	#if from or to locations were changed
	elif prev_to != new_to:
		prev_to = new_to
		prev_path = get_shortest_path(name_vs_node[prev_from], name_vs_node[prev_to])
		curr_loc = 0
	elif prev_from != new_from:
		prev_from = new_from
		prev_path = get_shortest_path(name_vs_node[prev_from], name_vs_node[prev_to])
		curr_loc = 0

	new_img = base64.b64encode(open('locs/{}.JPG'.format(prev_path[curr_loc]),'rb').read())
	direction = directions[int(prev_path[curr_loc]),int(prev_path[curr_loc+1])]
	print("Curr_loc{}".format(curr_loc))
	return [html.Img(src='data:image/png;base64,{}'.format(new_img.decode()), style={'display':'block', 'margin-left':'auto', 'margin-right':'auto','width':'45%'}),
	html.Div([direction])]




if __name__ == '__main__':
	app.run_server(debug=True, host='0.0.0.0')
