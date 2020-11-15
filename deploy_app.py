import base64

import dash
import random
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graph_computation
from random import randrange
import datetime

#empty_graph
empty_graph = go.Figure()
# external layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# init
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}]
                )
loc_info = pd.read_csv('dbs/special_nodes.csv')
graph = pd.read_csv("dbs/nodes.csv", index_col=None)
directions = graph.set_index(['From', 'To']).to_dict()['direction']
name_vs_node = loc_info.dropna().set_index('Name').to_dict()['Node']
# configuring logo
encoded_klinik_logo = base64.b64encode(open('logos/klinik.png', 'rb').read())

visit_df = pd.read_csv("dbs/visit_data.csv")
df = visit_df.groupby(["day", "dest"]).count().reset_index()
fig1 = px.bar(df, x='day', y='gender', color="dest",
              title='Visit count for the past week',
              labels={"day": "Day of week", "dest": "Destination", "gender": "Visitor count"},
              hover_name='day', hover_data = ['day','dest'])
loc_vs_color = {}
for bar in fig1.data:
    marker = bar['marker']
    loc_vs_color[bar['offsetgroup']] = marker['color']
#init app
app.layout = html.Div([
    # title and logo

    html.Div([
        html.Div([
            html.Div([
                html.Img(src='data:image/png;base64,{}'.format(encoded_klinik_logo.decode()),
                         style={'width': '350', 'height': '68px', 'float': 'left'}),
                html.H1(children='Westpfalz Klinikum WayFinder',
                        style={'fontSize': 24, 'text-align': 'center', 'padding-right': '60px',
                               'padding-top': '40px'})
            ])
        ], className='row'
        ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Navigation",
                    children=[
                        html.Div([
                            html.H2(children='From', style={'fontSize': 24, 'padding-left': '40px', 'float': 'left'}),
                            html.H2(children='To', style={'fontSize': 24, 'padding-right': '80px', 'float': 'right'})
                        ],
                            className='row', style={'padding-top': '40px'}),
                        html.Div([
                            html.Div(
                                dcc.Dropdown(id='from',
                                             options=[
                                                 {'label': 'ToiletI', 'value': 'ToiletI'},
                                                 {'label': 'ToiletII', 'value': 'ToiletII'},
                                                 {'label': 'Entrance', 'value': 'Entrance'},
                                                 {'label': 'X-ray room', 'value': 'X-ray room'},
                                                 {'label': 'Cafeteria', 'value': 'Cafeteria'}
                                             ],
                                             value='ToiletI'
                                             ), className='pretty_container four columns',
                                style={'padding-left': '40px'}),
                            html.Div(
                                dcc.Dropdown(id='to',
                                             options=[
                                                 {'label': 'ToiletI', 'value': 'ToiletI'},
                                                 {'label': 'ToiletII', 'value': 'ToiletII'},
                                                 {'label': 'Entrance', 'value': 'Entrance'},
                                                 {'label': 'X-ray room', 'value': 'X-ray room'},
                                                 {'label': 'Cafeteria', 'value': 'Cafeteria'}
                                             ],
                                             value='Entrance'
                                             ), className='pretty_container four columns',
                                style={'width': '350', 'height': '68px', 'float': 'right', 'padding-right': '40px'})
                        ], style={'padding-top': '20px'}, className='row'),
                        # Testing directions
                        # full slides
                        html.Div(children=[
                            html.Div(html.A(["☜"], id='prev_loc',
                                            style={'text-decoration': 'None', 'font-size': '78px',
                                                   'vertical-align': 'middle'}),
                                     style={'float': 'left'}),
                            html.Div(html.A(["☞"], id='next_loc',
                                            style={'text-decoration': 'None', 'font-size': '78px',
                                                   'vertical-align': 'middle'}),
                                     style={'float': 'right'}),
                            html.Div(id='loc_img')
                        ], className='row')
                    ]
                ),
                dcc.Tab(
                    label="Show on map",
                    children=[
                        html.Div(
                            [
                                html.Img(
                                    src="https://uploads-ssl.webflow.com/5836aa64e1025f0e4d9296d3/584041151141e61b0ad41460_Indoor%20Map%20Indoor%20Location%20St%20Olavs%20Hospital%20DEMO%201%20-%20360.gif")
                            ],
                            style={"width": "60%","padding": "10px"}
                        )
                    ]
                ),
                dcc.Tab(
                    label='Staff View',
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="day_visit_histogram",
                                            figure=fig1,
                                            style={"width": "50%"}
                                        ),
                                        dcc.Graph(
                                            id="visitor_pattern",
                                            figure={},
                                            style={"width": "50%"}
                                        )
                                    ],
                                    style={"display": "flex"}
                                )
                            ]
                        )
                    ]
                )

            ]
        ),

    ]
    )
]
)


def get_shortest_path(_from, to):
    return graph_computation.dijkstra(str(_from), str(to), graph)


curr_loc = 0
prev_loc = 11
next_loc = 1
prev_to = 'ToiletI'
prev_from = 'ToiletII'
prev_path = ['1', '2', '5', '9']

def calc_visitor_count_for_day(day, dest):
    def random_date(start,l):
        current = start
        while l >= 0:
            current = current + datetime.timedelta(minutes=randrange(10))
            yield current
            l-=1
    res = pd.DataFrame(columns= ['count', 'time'] )
    startDate = datetime.datetime.now()
    times = []
    counts = []
    for x in list(random_date(startDate,200)):
        times.append(x.strftime("%d/%m/%y %H:%M"))
    counts = random.sample(range(200, 500), len(times)//2)
    counts.extend(random.sample(range(10, 250), len(times)//2+1))
    res['count'] = counts
    res['time'] = times
    return res



@app.callback(
dash.dependencies.Output('visitor_pattern', 'figure'),
[dash.dependencies.Input('day_visit_histogram','clickData')]
)
def update_visitor_pattern(selectedData):
    if selectedData is None:
        return empty_graph
    day, dest = selectedData['points'][0]['customdata'][0],selectedData['points'][0]['customdata'][1]
    df = calc_visitor_count_for_day(day, dest)
    fig = px.line(df, x='time', y="count" ,title = f"Visitor pattern at location {dest} for {day}")
    fig['data'][0]['line']['color'] = loc_vs_color[dest]
    return fig

@app.callback(
    dash.dependencies.Output('loc_img', 'children'),
    [dash.dependencies.Input('prev_loc', 'n_clicks'),
     dash.dependencies.Input('next_loc', 'n_clicks'),
     dash.dependencies.Input('to', 'value'),
     dash.dependencies.Input('from', 'value')])
def update_output(new_prev_loc, new_next_loc, new_to, new_from):
    if new_to is None or new_from is None:
        return dash.no_update
    global prev_loc, next_loc, curr_loc, prev_to, prev_from, prev_path
    # if prev or next was changed
    if prev_loc != new_prev_loc:
        prev_loc = new_prev_loc
        curr_loc -= 1
        curr_loc %= len(prev_path)
    elif next_loc != new_next_loc:
        next_loc = new_next_loc
        curr_loc += 1
        curr_loc %= len(prev_path)
    # if from or to locations were changed
    elif prev_to != new_to:
        prev_to = new_to
        prev_path = get_shortest_path(name_vs_node[prev_from], name_vs_node[prev_to])
        curr_loc = 0
    elif prev_from != new_from:
        prev_from = new_from
        prev_path = get_shortest_path(name_vs_node[prev_from], name_vs_node[prev_to])
        curr_loc = 0

    new_img = base64.b64encode(open('locs/{}.png'.format(prev_path[curr_loc]), 'rb').read())
    try:
        direction = directions[int(prev_path[curr_loc]), int(prev_path[curr_loc + 1])]
        return [
        html.Div([direction.upper()], style={'text-align':'center', 'font-size':'150%'}),
        html.Img(src='data:image/png;base64,{}'.format(new_img.decode()),
                         style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '45%'})
                         ]

    except Exception as e:
        print(e)
        return [html.Img(src='data:image/png;base64,{}'.format(new_img.decode()),
                         style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '45%'}),
                ]


if __name__ == '__main__':
    app.run_server(debug=True,
                   host='0.0.0.0',
                   threaded=False
                   )
