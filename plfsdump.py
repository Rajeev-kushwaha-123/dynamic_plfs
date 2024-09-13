import pandas as pd
import dash
from dash import Dash, Input, Output, dcc, html
import os
from sqlalchemy import create_engine
import plotly.graph_objs as go
import plotly.io as pio
import io
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv 
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Construct database URL from environment variables
db_url = create_engine(f"{os.getenv('ENGINE')}://{os.getenv('DTABASE_USER')}:{os.getenv('PASSWORD')}@{os.getenv('HOST')}/{os.getenv('PLFS_DATABASE')}")
# db_url = 'postgresql://postgres:postgres@127.0.0.1:5432/plfs_db'

query= '''	
select
    pf.plfs_fact_code,
	pf.religion_code,
    pf.indicator_code,
    pf.indicator_value, 
    pf.age_group_code,
    pf.gender_code,
    pf.state_code,
    pf.quarter_code,
    pf.disaggregation_level_code,
    pf.industry_code,
    pf.umpce_code,
    pf.sector_code,
    pf.work_industry_code,
    pf.enterprise_type_code,
    pf.self_employment_code,
    pf.occupation_divisions_code,
    pf.broad_employment_code,
    pf.education_level_code,
    pf.frequency_code,
    pf.year,
	pf.religion_code,
	pf.social_group_code,
	pf.job_contract_code,
	pf.nic2_industry_code,
	pf.hour_working_code,
	pf.sub_self_employment_code,
	pf.nic_code,
	nc.description as nic_description,
	sse.sub_self_employment_name as sub_self_employment_description,
	ni.nic2_industry_name as nic2_industry_description,
	hw.hour_working_name as  hour_working_description,
	jb.job_contract_name as job_contract_description,
	sg.social_group_name as social_group_description,
	i.indicator_display_name as indicator_display_description,
	rc.religion_name as religion_description,
    a.agegroup_name AS age_group_description,
    slf.self_employment_name AS self_employment_description,
    ind.industry_name AS industry_description,
    w.work_industry_name AS work_industry_description,
    dis.disaggregation_level AS disaggregation_level_description,
    f.frequency_name AS frequency_description,
    x.gender_name AS gender_description,
    e.education_level_name AS education_level_description,
    i.indicator_name AS indicator_description,
    q.quarter_name AS quarter_description,
    s.state_name AS state_description,
    u.umpce_name AS umpce_description,
    st.status_name AS status_description,
    o.occupation_divisions_name AS occupation_divisions_description,
    en.enterprise_type_name AS enterprise_type_description,
    be.broad_employment_name AS broad_employment_description,
    sec.sector_name AS sector_description,
    i.status as indicator_status
FROM
    plfs_fact AS pf
LEFT JOIN
    age_group AS a ON pf.age_group_code = a.agegroup_code
LEFT JOIN
    industry AS ind ON pf.industry_code = ind.industry_code
LEFT JOIN
    education_level AS e ON pf.education_level_code = e.education_level_code
LEFT JOIN
    indicator AS i ON pf.indicator_code = i.indicator_code
LEFT JOIN
    "state" AS s ON pf.state_code = s.state_code
LEFT JOIN
    self_employment AS slf ON pf.self_employment_code = slf.self_employment_code
LEFT JOIN
    enterprise_type AS en ON pf.enterprise_type_code = en.enterprise_type_code
LEFT JOIN
    status_code AS st ON pf.status_code = st.status_code
LEFT JOIN
    sector AS sec ON pf.sector_code = sec.sector_code
LEFT JOIN
    gender AS x ON pf.gender_code = x.gender_code
LEFT JOIN
    occupation_divisions AS o ON pf.occupation_divisions_code = o.occupation_divisions_code
LEFT JOIN
    frequency AS f ON pf.frequency_code = f.frequency_code
LEFT JOIN
    quarter AS q ON pf.quarter_code = q.quarter_code
LEFT JOIN
    umpce AS u ON pf.umpce_code = u.umpce_code
LEFT JOIN
    broad_employment AS be ON pf.broad_employment_code = be.broad_employment_code
LEFT JOIN
    work_industry AS w ON pf.work_industry_code = w.work_industry_code
LEFT JOIN
    disaggregation_level AS dis ON pf.disaggregation_level_code = dis.disaggregation_level_code
Left join 
     religion as rc on pf.religion_code=rc.religion_code
left join 
   social_group as sg on pf.social_group_code=sg.social_group_code
left join
  job_contract as jb on pf.job_contract_code=jb.job_contract_code
left join
   industry_nic_2 as ni on  pf.nic2_industry_code= ni.nic2_industry_code
left join
    hour_working as hw on pf.hour_working_code=hw.hour_working_code
left join 
  sub_self_employment as sse on pf.sub_self_employment_code::bigint =sse.sub_self_employment_code
left join
   nic as nc on pf.nic_code=nc.nic_code

    where i.status = 'Active'
'''
df = pd.read_sql_query(query, db_url)
#df.to_csv('plfs_db_result.csv')
# df = pd.read_csv("plfs_db_result.csv")


#sorting indicator on the basis of indicator code 
indicator_df = df[["indicator_code","indicator_description","indicator_status","indicator_display_description"]]
indicator_df.indicator_code= pd.to_numeric(indicator_df.indicator_code, errors='coerce')
indicator_df = indicator_df[indicator_df['indicator_status'] == 'Active']
indicator_df = indicator_df.sort_values(by="indicator_code")

#sorting state on the basis of state code 
filtered_df1=df[["state_code","state_description"]]
filtered_df1.state_code=pd.to_numeric(filtered_df1.state_code,errors='coerce')
filtered_df1=filtered_df1.sort_values(by="state_code")



# sorting year 
df=df.sort_values(by='year')

#print('LABEL VALUE',str({'label': i, 'value': i} for i in df['age_group_description'].unique()))

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
    {
        "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
        "rel": "stylesheet",
    },
]

# Define default dropdown values function
def get_default_dropdown_values():
    default_indicator = "Labour Force Participation Rate"
    default_state = 'All India'
    default_sector = 'Rural + Urban'
    default_status = 'Current Weekly Status (CWS)'
    default_gender = 'Person'
    default_year = ["Select All"]
    default_age_group = "All Ages"
    default_education_level = " "
    default_industry = "Agriculture, forestry and fishing"
    default_occupation_divisions = "All"
    default_enterprise_type ="Total "
    default_work_industry = "Seconday"
    default_broad_employment = "All"
    default_self_employment = "Self-Employed"
    default_quarter ="Jan-Mar"
    default_disaggregation_level ="Broad status in employment"
    default_umpce ="all"
    default_religion='Hinduism'
    default_job_contract="Not eligible for paid leave"
    default_industry_nic_2='05-09 (mining & quarrying)'
    default_hour_working="All"
    default_sub_self_employment="Own account worker, employer"
    
   
    
    return (default_indicator, default_state, default_sector, default_gender, default_year, default_status,
            default_age_group, default_education_level, default_industry, default_occupation_divisions,
            default_enterprise_type, default_work_industry, default_broad_employment, default_self_employment,
            default_quarter,default_disaggregation_level,default_umpce,default_religion, 
            default_job_contract, default_industry_nic_2,default_hour_working,default_sub_self_employment)

# Get default dropdown values
(default_indicator, default_state, default_sector, default_gender, default_year, default_status,
 default_age_group, default_education_level, default_industry, default_occupation_divisions,
 default_enterprise_type, default_work_industry, default_broad_employment, default_self_employment,
 default_quarter,default_disaggregation_level,default_umpce,default_religion,
 default_job_contract, default_industry_nic_2,default_hour_working,default_sub_self_employment) = get_default_dropdown_values()



def get_status_dropdown(selected_indicator):
    # Define the indicators that should return 'Usual Status (PS + SS)'
    indicators_for_usual_status = [
        
    ]
    
    # Check if the selected_indicator is in the list
    if selected_indicator in indicators_for_usual_status:
        return 'Usual Status (PS + SS)'
    else:
        return 'Current Weekly Status (CWS)'

selected_indicator = 'Labour Force Participation Rate'
default_status_value = get_status_dropdown(selected_indicator)
print('THE DEFAULT VALUE OF PDW SHOULD BE USUAL STATUS:',default_status_value)
# Test cases to verify the function works as expected
print(get_status_dropdown('Percentage distribution of workers'))  # Should print: 'Usual Status (PS + SS)'
print(get_status_dropdown('Percentage of regular wage/ salaried employees in non-agriculture sector'))  # Should print: 'Usual Status (PS + SS)'
print(get_status_dropdown('Labour Force Participation Rate'))  # Should print: 'Current Weekly Status (CWS)'
print(get_status_dropdown('Other Indicator'))  # Should print: 'Current Weekly Status (CWS)'


    
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "PLFS"

app.layout = html.Div(
    className="content-wrapper",
    children=[
        html.Div(
            style={'flex': '0 1 320px', 'padding': '10px', 'boxSizing': 'border-box'},
            children=[
                html.H1(
                    "Select Parameters to Get Chart",
                    className="parameter-data",
                    style={'fontSize': '15px', 'fontWeight': 'normal', 'marginBottom': '0px', 'marginTop': '20px'}
                ),
                html.Div(
                    children=[
                        html.Div(children="Indicator", className="menu-title"),
                        dcc.Dropdown(
                            id="indicator-dropdown",
                            options=[{'label': i, 'value': j} for i,j in zip(indicator_df["indicator_display_description"].unique(),indicator_df["indicator_description"].unique())],
                            
                            placeholder="Indicator",
                            searchable=False,
                            clearable=False,
                            className="dropdown",
                            value= default_indicator,
                            style={ "fontSize": "12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}                    
                ),
                html.Div(
                         id="age-group-container",
                     children=[
                         html.Div(children="Age-group", className="menu-title"),
                         dcc.Dropdown(
                                id="age-group-dropdown",
                              options=[{'label': i, 'value': i} for i in df['age_group_description'].unique()],
                             placeholder="Age-group",
                               searchable=False,
                             clearable=False,
                               className="dropdown",
                              value=default_age_group,  # Set default value
                                 style={"fontSize": "12px"}
                            ),
                    ],
                         style={'marginBottom': '0px'}
                        ),
                html.Div(
                     id="gender-container",
                     style={'marginBottom': '0px'},
                     children=[
                        html.Div(children="Gender", className="menu-title"),
                        dcc.Dropdown(
                            id="gender-dropdown",
                            options=[{'label': i, 'value': i} for i in df['gender_description'].unique()],
                            clearable=False,
                            placeholder="Gender",
                            searchable=False,
                            className="dropdown",
                            value= default_gender,
                            style={"fontSize": "12px"}
                        ),
                    ],
                ),
                 html.Div(
                     id="quarter-container",
                     style={'marginBottom': '0px'},
                    children=[
                        html.Div(children="Quarter", className="menu-title"),
                        dcc.Dropdown(
                            id="quarter-dropdown",
                            options=[{'label': i, 'value': i} for i in df['quarter_description'].unique()],
                            clearable=False,
                            placeholder="Quarter",
                            searchable=False,
                            className="dropdown",
                            value= default_quarter,
                            style={"fontSize": "12px"}
                        ),
                    ],
                ),
                  html.Div(
                     id="disaggregation-level-container",
                     style={'marginBottom': '0px'},
                    children=[
                        html.Div(children="Disaggregation Level", className="menu-title"),
                        dcc.Dropdown(
                            id="disaggregation-level-dropdown",
                            options=[{'label': i, 'value': i} for i in df['disaggregation_level_description'].unique()],
                            clearable=False,
                            placeholder="Dissagregation-level",
                            searchable=False,
                            className="dropdown",
                            value= default_disaggregation_level,
                            style={"fontSize": "12px"}
                        ),
                    ],
                ),
                html.Div(
                     id="umpce-container",
                     style={'marginBottom': '0px'},
                    children=[
                        html.Div(children="Umpce", className="menu-title"),
                        dcc.Dropdown(
                            id="umpce-dropdown",
                            options=[{'label': i, 'value': i} for i in df['umpce_description'].unique()],
                            clearable=False,
                            placeholder="umpce",
                            searchable=False,
                            className="dropdown",
                            value= default_umpce,
                            style={"fontSize": "12px"}
                        ),
                    ],
                ),
                
                html.Div(
                    id="state-container",
                    children=[
                        html.Div(children="State", className="menu-title"),
                        dcc.Dropdown(
                            id="state-dropdown",
                            options=[{'label': i, 'value': i} for i in filtered_df1['state_description'].unique()],
                            clearable=False,
                            placeholder="State",
                            searchable=False,
                            className="dropdown",
                            value= default_state,
                            style={"fontSize": "12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="sector-container",
                    children=[
                        html.Div(children="Sector", className="menu-title"),
                        dcc.Dropdown(
                            id="sector-dropdown",
                            options=[{'label': i, 'value': i} for i in df['sector_description'].unique()],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="Sector",
                            value=default_sector
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="industry-container",
                    style={'display':"none",'marginBottom': '0px'},
                    children=[
                        html.Div(children="Industry", className="menu-title"),
                        dcc.Dropdown(
                            id="industry-dropdown",
                            options=[{'label': i, 'value': i} for i in df['industry_description'].unique()],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="industry",
                            value=default_industry
                        ),
                    ],
                    
                ),
                html.Div(
                    id="work-industry-container",
                    style={'display':"none",'marginBottom': '0px'},
                    children=[
                        html.Div(children="Work Industry", className="menu-title"),
                        dcc.Dropdown(
                            id="work-industry-dropdown",
                            options=[{'label': i, 'value': i} for i in df['work_industry_description'].unique()],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="work_industry",
                            value=default_work_industry
                        ),
                    ],
                 
                ),
                html.Div(
                    id="enterprise-type-container",
                    style={'display':"none",'marginBottom': '0px'},
                    children=[
                        html.Div(children="Enterprise Type", className="menu-title"),
                        dcc.Dropdown(
                            id="enterprise-type-dropdown",
                            options=[{'label': i, 'value': i} for i in df['enterprise_type_description'].unique()],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="enterprise_type",
                            value=default_enterprise_type
                        ),
                    ],
                   
                ),
                html.Div(
                    id="self-employment-container",
                    style={'display':"none",'marginBottom': '0px'},
                    children=[
                        html.Div(children="Self Employment", className="menu-title"),
                        dcc.Dropdown(
                            id="self-employment-dropdown",
                            options=[{'label': i, 'value': i} for i in df['self_employment_description'].unique()],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="self_employment",
                            value=default_self_employment
                        ),
                    ],
                   
                ),
                html.Div(
                    id="occupation-divisions-container",
                    style={'display':"none",'marginBottom': '0px'},
                    children=[
                        html.Div(children="Occupation Divisions", className="menu-title"),
                        dcc.Dropdown(
                            id="occupation-divisions-dropdown",
                            options=[{'label': i, 'value': i} for i in df['occupation_divisions_description'].unique()],
                            clearable=False,
                            placeholder="occupation_divisions",
                            searchable=False,
                            className="dropdown",
                            value=default_occupation_divisions,
                            style={"fontSize": "12px"}
                        ),
                    ],
                   
                ),
                html.Div(
                    id="broad-employment-container",
                    style={'display':"none",'marginBottom': '0px'},
                    children=[
                        html.Div(children="Broad Employment", className="menu-title"),
                        dcc.Dropdown(
                            id="broad-employment-dropdown",
                            options=[{'label': i, 'value': i} for i in df['broad_employment_description'].unique()],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="broad_employment",
                            value=default_broad_employment
                        ),
                    ],
                  
                ),
                html.Div(
                    id="education-level-container",
                    children=[
                        html.Div(children="Education Level", className="menu-title"),
                        dcc.Dropdown(
                            id="education-level-dropdown",
                            options=[{'label': i, 'value': i} for i in df['education_level_description'].unique()],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="education_level",
                            value=default_education_level
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
        
                html.Div(
                    id="year-container",
                    children=[
                        html.Div(children="Year", className="menu-title"),
                        dcc.Dropdown(
                            id="year-dropdown",
                            options=[{'label': 'Select All', 'value': 'Select All'}] + [{'label': str(year), 'value': year} for year in df['year'].unique()],
                            multi=True,
                            className="dropdown",
                            clearable=False,
                            searchable=False,
                            placeholder="Select Year",
                            value=default_year
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="status-container",
                    children=[
                        html.Div(children="Status", className="menu-title"),
                        dcc.Dropdown(
                            id="status-dropdown",
                            options=[{'label': i, 'value': i} for i in df['status_description'].unique()],
                            multi=False,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="Status",
                            value=default_status
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="religion-container",
                    children=[
                        html.Div(children="Religion", className="menu-title"),
                        dcc.Dropdown(
                            id="religion-dropdown",
                            options=[{'label': str(status), 'value': status} for status in df['religion_description'].unique()],
                            multi=False,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="religion",
                            value=default_religion
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                    html.Div(
                    id="job-contract-container",
                    children=[
                        html.Div(children="Job Contract", className="menu-title"),
                        dcc.Dropdown(
                            id="job-contract-dropdown",
                            options=[{'label': str(status), 'value': status} for status in df['job_contract_description'].unique()],
                            multi=False,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="job_contract",
                            value=default_job_contract,
                            style={"fontSize": "10px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="industry-nic2-container",
                    children=[
                        html.Div(children="Nic2 Industry", className="menu-title"),
                        dcc.Dropdown(
                            id="nic2-industry-dropdown",
                            options=[{'label': str(status), 'value': status} for status in df['nic2_industry_description'].unique()],
                            multi=False,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="nic2_industry",
                            value=default_industry_nic_2
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    id="hour-working-container",
                    children=[
                        html.Div(children="Hour Working", className="menu-title"),
                        dcc.Dropdown(
                            id="hour-working-dropdown",
                            options=[{'label': str(status), 'value': status} for status in df['hour_working_description'].unique()],
                            multi=False,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="hour_working",
                            value=default_hour_working
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                   html.Div(
                    id="sub-self-employment-container",
                    children=[
                        html.Div(children="Sub Self Eemployment", className="menu-title"),
                        dcc.Dropdown(
                            id="sub-self-employment-dropdown",
                            options=[{'label': str(status), 'value': status} for status in df['sub_self_employment_description'].unique()],
                            multi=False,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            placeholder="sub-self-employment",
                            value=default_sub_self_employment
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Button(
                    'Apply', id='plot-button', n_clicks=0, className='mr-1',
                    style={
                        'width': '100%',
                        'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'text-align': 'center',
                        'text-decoration': 'none',
                        'display': 'inline-block',
                        'font-size': '16px',
                        'margin': '15px 0',
                        'cursor': 'pointer',
                        'border-radius': '8px',
                        'marginTop': '30px',
                        'marginBottom': '0px'
                    }
                ),
               # Inside app.layout within the HTML structure where buttons are placed
                html.A(html.Button(
                       'Reset', id='reset-button', n_clicks=0, className='mr-1',
                        style={
                          'width': '100%',
                          'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                         'color': 'white',
                         'border': 'none',
                         'padding': '10px 20px',
                         'text-align': 'center',
                         'text-decoration': 'none',
                          'display': 'inline-block',
                          'font-size': '16px',
                          'margin': '15px 0',
                          'cursor': 'pointer',
                           'border-radius': '8px',
                           'marginTop': '30px',
                         'marginBottom': '0px'
                      }
                ),href='/viz/plfs/'),
                html.Button(
                    'Download', id='download-svg-button', n_clicks=0, className='mr-1',
                    style={
                        'width': '100%',
                        'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'text-align': 'center',
                        'text-decoration': 'none',
                        'display': 'inline-block',
                        'font-size': '16px',
                        'margin': '20px 0',
                        'cursor': 'pointer',
                        'border-radius': '8px',
                        'marginBottom': '0px'
                    }
                ),
            ]
        ),
        # Graph area
        html.Div(
            style={'flex': '1', 'padding': '20px', 'position': 'relative', 'text-align': 'center', 'height': 'calc(100% - 50px)'},
            children=[
                dcc.Loading(
                    id="loading-graph",
                    type="circle", color='#83b944',
                    children=[
                        html.Div(
                            id='graph-container',
                            style={'width': '100%', 'height': '650px'},
                            children=[
                                html.Div(
                                    className="loader",
                                    id="loading-circle",
                                    style={"position": "absolute", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"}
                                ),
                                dcc.Graph(
                                    id="plot-output",
                                    config={"displayModeBar": False},
                                    style={'width': '100%', 'height': 'calc(100% - 50px)'}
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        ),
        dcc.Download(id="download"),
        # Interval component to trigger default plot
        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # Interval in milliseconds
            n_intervals=0,
            max_intervals=1  # Ensure it runs only once
        )
    ]
)
@app.callback(
    Output("state-container", "style"),
    Output("sector-container", "style"),
    Output("year-container", "style"),
    Output("status-container", "style"),
    Output("age-group-container", "style"),
    Output("gender-container", "style"),
    Output("education-level-container","style"),
    Output("industry-container", "style"), 
    Output("occupation-divisions-container","style"),
    Output("enterprise-type-container","style"),
    Output("work-industry-container", "style"),
    Output("broad-employment-container","style"),
    Output("self-employment-container","style"),
    Output("quarter-container","style"),
    Output("disaggregation-level-container","style"),
    Output("umpce-container","style"),
    Output("religion-container","style"),
    Output("job-contract-container","style"),
    Output("industry-nic2-container","style"),
    Output("hour-working-container","style"),
    Output("sub-self-employment-container","style"),
    Output("status-container","children"),
    [Input("indicator-dropdown", "value")]
)
def update_dropdown_visibility(indicator):
    print("UPDATE DROPDOWN VISIBILITY ACCORDING TO INDICATOR SELECTED BY USER!")
    if indicator in ['Labour Force Participation Rate', 'Worker Population Ratio', 'Unemployment Rate']: 
        return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'block'},  # age-group-dropdown
            {'display': 'block'},  # gender-dropdown
            {'display': 'block'},  # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'none'},    #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'},      #religion-dropdown
            {'display':'none'},      #job-contract-dropdown
            {'display':'none'},     #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Percentage distribution of persons in labour force":
         
         return(
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},    #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown 
            {'display': 'none'} ,    #umpce-dropdown 
            {'display':'none'},       #religion-dropdown
            {'display':'none'},      #job-contract-dropdown
            {'display':'none'},      #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
         )
    elif indicator == "Percentage of regular wage/ salaried employees in non-agriculture sector ":
        return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'none'},    #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'} ,    #umpce-dropdown
            {'display':'none'},      #religion-dropdown
            {'display':'block'},       #job-contract-dropdown
            {'display':'none'},      #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Usual Status (PS + SS)"),]
        )
    elif indicator=="Average wage/salary earnings (Rs. 0.00) during the preceding calendar month from regular wage/salaried  employment among the regular wage/salaried employees":
        return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},    #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'} ,    #umpce-dropdown
            {'display':'none'},     #religion-dropdown
            {'display':'none'} ,      #job-contract-dropdown
            {'display':'none'},     #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Average wage/salary earnings (Rs. 0.00) per day from casual labour work other than public works in CWS":
        return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},    #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'},       #religion-dropdown
            {'display':'none'},       #job-contract-dropdown
            {'display':'none'},     #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Average gross earnings (Rs. 0.00) during last 30 days from self-employment among self-employed persons":
        return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},    #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},    #umpce-dropdown
            {'display':'none'},       #religion-dropdown
            {'display':'none'},       #job-contract-dropdown
            {'display':'none'},      #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Average no. of hours available for additional work in a week (0.0) for person with broad status in employment in CWS":
        return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'block'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},   #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'}  ,   #umpce-dropdown
            {'display':'none'}  ,     #religion-dropdown
            {'display':'none'} ,      #job-contract-dropdown
            {'display':'none'},      #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Percentage of workers available for additional work during the week for person with broad status in employment in CWS":
        return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'block'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},   #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'}  ,     #religion-dropdown
             {'display':'none'} ,     #job-contract-dropdown
            {'display':'none'},      #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Percentage distribution of workers":
        return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'block'},    # self-employment-dropdown
            {'display': 'none'},   #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'},     #religion-dropdown
            {'display':'none'},       #job-contract-dropdown
            {'display':'none'},     #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'block'},       # sub-self-employment-dropdown
            #Logic below to set Status to Usual Status for TWO SPECIFIC INDICATORS which only have Data in CWS
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Usual Status (PS + SS)"),]
    
        )
    
    elif indicator=="Average wage earnings (Rs.) per day from casual labour work":
            return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'none'},   #quarter-dropdown
            {'display': 'block'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'} ,      #religion-dropdown
            {'display':'none'} ,      #job-contract-dropdown
            {'display':'none'},    #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Average no. of days worked in a week (0.0) for person with broad status in employment in CWS":
         return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'block'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},   #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'} ,      #religion-dropdown
            {'display':'none'} ,      #job-contract-dropdown
            {'display':'none'},      #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    
    elif indicator=='Average no. of days actually worked in a week (0.0) for person with broad status in employment in CWS':
             return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'block'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},   #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'} ,      #religion-dropdown
            {'display':'none'} ,      #job-contract-dropdown
            {'display':'none'},      #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Percentage  distribution of usually working persons":
             return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'block'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'none'},   #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'} ,      #religion-dropdown
            {'display':'none'} ,      #job-contract-dropdown
            {'display':'none'},      #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Percentage distribution of  person working":
             return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'block'},    # self-employment-dropdown
            {'display': 'none'},   #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'} ,      #religion-dropdown
            {'display':'none'} ,      #job-contract-dropdown
            {'display':'none'},     #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'block'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    elif indicator=="Average number of hours (0.0) actually worked per week considering all the economic activities performed during the week for person with broad status in employment in CWS":
            return (
            {'display': 'block'},  # state-dropdown
            {'display': 'block'},  # sector-dropdown
            {'display': 'block'},  # year-dropdown
            {'display': 'block'},  # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'block'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'block'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'block'},   #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},     #umpce-dropdown
            {'display':'none'} ,      #religion-dropdown
            {'display':'none'} ,      #job-contract-dropdown
            {'display':'none'},    #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )
    
    

    
    else:
        return (
            {'display': 'none'},   # state-dropdown
            {'display': 'none'},   # sector-dropdown
            {'display': 'none'},   # year-dropdown
            {'display': 'none'},   # status-dropdown
            {'display': 'none'},   # age-group-dropdown
            {'display': 'none'},   # gender-dropdown
            {'display': 'none'},   # education-level-dropdown
            {'display': 'none'},   # industry-dropdown
            {'display': 'none'},   # occupation-divisions-dropdown
            {'display': 'none'},   # enterprise-type-dropdown
            {'display': 'none'},   # work-industry-dropdown
            {'display': 'none'},   # broad-employment-dropdown
            {'display': 'none'},    # self-employment-dropdown
            {'display': 'none'},    #quarter-dropdown
            {'display': 'none'},    #disaggregation-level-dropdown  
            {'display': 'none'},    #umpce-dropdown
            {'display':'none'},      #religion-dropdown
            {'display':'none'},       #job-contract-dropdown
            {'display':'none'},     #nic2-industry-dropdown
            {'display':'none'},       #hour-working-dropdown
            {'display':'none'},       # sub-self-employment-dropdown
            [html.Div(children="Status", className="menu-title"),dcc.Dropdown(id="status-dropdown",options=[{"label": i, "value": i} for i in df["status_description"].unique()],multi=False,clearable=False,searchable=False,className="dropdown",placeholder="Status",value="Current Weekly Status (CWS)"),]
        )

@app.callback(
    Output("plot-output", "figure"),
    [Input('plot-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State("indicator-dropdown", "value"),
     State("state-dropdown", "value"),
     State("sector-dropdown", "value"),
     State("gender-dropdown", "value"),
     State("year-dropdown", "value"),
     State("status-dropdown", "value"),
     State("age-group-dropdown", "value"),
     State("education-level-dropdown", "value"),
     State("industry-dropdown", "value"),
     State("occupation-divisions-dropdown", "value"),
     State("enterprise-type-dropdown", "value"),
     State("work-industry-dropdown", "value"),
     State("broad-employment-dropdown", "value"),
     State("self-employment-dropdown", "value"),
     State('quarter-dropdown','value'),
     State('disaggregation-level-dropdown','value'),
     State('umpce-dropdown','value'),
     State("religion-dropdown","value"),
     State("job-contract-dropdown","value"),
     State("nic2-industry-dropdown","value"),
     State("hour-working-dropdown","value"),
     State("sub-self-employment-dropdown","value")]
)

def update_plot(n_clicks, n_intervals, indicator, state, sector, gender, year, status, 
                age_group, education_level, industry, occupation_divisions, 
                enterprise_type, work_industry, broad_employment, self_employment,
                quarter,disaggregation_level,umpce,religion,job_contract,nic2_industry,hour_working,sub_self_employment):
    
    print('Plotting Graph Now')
    ctx = dash.callback_context
    button_id = None
    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
    print('==>button_id:', n_clicks, 
          '==>indicator:', indicator, 
          '==>state:', state, 
          '==>gender:', gender, 
          '==>status:', status, 
          '==>year:', year, 
          '==>education_level:', education_level, 
          '==>sector:', sector, 
          '==>age_group:', age_group, 
          '==>industry:', industry, 
          '==>occupation_divisions:', occupation_divisions, 
          '==>enterprise_type:', enterprise_type, 
          '==>work_industry:', work_industry, 
          '==>broad_employment:', broad_employment, 
          '==>self_employment:', self_employment, 
          '==>quarter:', quarter, 
          '==>disaggregation_level:', disaggregation_level, 
          '==>umpce:', umpce,
          '==>religion:',religion,
          "==>job-contract:",job_contract,
          "==>nic2-industry:",nic2_industry,
          "==>hour-working:",hour_working,
          '==>sub-self-employment',sub_self_employment)
    
    # Debug: Print the DataFrame before filtering
    print("Initial DataFrame head:\n", df.head())

    # Initial common filtering
    filtered_df = df[
        (df['indicator_description'] == indicator) &
        (df['state_description'] == state) & 
        (df['gender_description'] == gender) & 
        (df['sector_description'] == sector) &
        (df['status_description'] == status)
    ]

    print('+++++++++++++++filtered_df:',filtered_df)
    # # Apply additional filters if values are provided
    if indicator in ['Labour Force Participation Rate', 'Worker Population Ratio', 'Unemployment Rate']: 
        if age_group is not None or age_group ==  "All Ages":
            filtered_df = filtered_df[filtered_df['age_group_description'] == age_group]
        elif age_group == None:
            filtered_df = filtered_df[(filtered_df['age_group_description'].isnull())]
            
        if education_level is not None :
            filtered_df = filtered_df[filtered_df['education_level_description'] == education_level]
        elif education_level == None or education_level == " ":
            filtered_df = filtered_df[(filtered_df['education_level_description'].isnull())]

        #Add logic to remove rows in filtered_df dataframe that contains NULL Value for religion_description
        filtered_df = filtered_df[(filtered_df['religion_description'].isnull())]
        filtered_df = filtered_df[(filtered_df['social_group_description'].isnull())]
        filtered_df = filtered_df[(filtered_df['disaggregation_level_description'].isnull())]
        filtered_df = filtered_df[(filtered_df['umpce_description'].isnull())]
        print("catch up the repeated problem in first three indicator:",filtered_df)
                  
    elif indicator=="Percentage distribution of persons in labour force":

        # if self_employment is not None or self_employment=="Self-Employed":
        #     filtered_df = filtered_df[filtered_df['self_employment_description'] == self_employment]

        # elif self_employment == None:
        #    filtered_df = filtered_df[(filtered_df['self_employment_description'].isnull())]
        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]
        

        

    elif indicator == "Percentage of regular wage/ salaried employees in non-agriculture sector ":

        if job_contract is not None or job_contract =="Not eligible for paid leave":
            filtered_df = filtered_df[filtered_df['job_contract_description'] == job_contract]

        elif job_contract == None:
            filtered_df = filtered_df[(filtered_df['job_contractr_description'].isnull())]
        
         
    elif indicator=="Average wage/salary earnings (Rs. 0.00) during the preceding calendar month from regular wage/salaried  employment among the regular wage/salaried employees":

        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]
    
    elif indicator=="Average wage/salary earnings (Rs. 0.00) per day from casual labour work other than public works in CWS":
        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]

        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]

    elif indicator=="Average gross earnings (Rs. 0.00) during last 30 days from self-employment among self-employed persons":

        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]

    elif indicator=="Average no. of hours available for additional work in a week (0.0) for person with broad status in employment in CWS":
        if broad_employment is not None or broad_employment=="All":
            filtered_df = filtered_df[filtered_df['broad_employment_description'] == broad_employment]
        elif broad_employment == None:
            filtered_df = filtered_df[(filtered_df['broad_employment_description'].isnull())]

        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]
        
        # if disaggregation_level is not None or disaggregation_level=="Broad status in employment":
        #     filtered_df = filtered_df[filtered_df['disaggregation_level_description'] == disaggregation_level]
        # elif disaggregation_level == None:
        #     filtered_df = filtered_df[(filtered_df['disaggregation_level_description'].isnull())]
    
    elif indicator=="Percentage of workers available for additional work during the week for person with broad status in employment in CWS":

        if broad_employment is not None or broad_employment=="All":
            filtered_df = filtered_df[filtered_df['broad_employment_description'] == broad_employment]
        elif broad_employment == None:
            filtered_df = filtered_df[(filtered_df['broad_employment_description'].isnull())]

        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]
        
        # if disaggregation_level is not None or disaggregation_level=="Broad status in employment":
        #     filtered_df = filtered_df[filtered_df['disaggregation_level_description'] == disaggregation_level]
        # elif disaggregation_level == None:
        #     filtered_df = filtered_df[(filtered_df['disaggregation_level_description'].isnull())]

    elif indicator=="Percentage distribution of workers":
        
        if self_employment is not None or self_employment=="Self-Employed":
            filtered_df = filtered_df[filtered_df['self_employment_description'] == self_employment]

        elif self_employment == None:
           filtered_df = filtered_df[(filtered_df['self_employment_description'].isnull())]

        if sub_self_employment is not None or sub_self_employment=="Own account worker, employer":

            filtered_df = filtered_df[filtered_df['sub_self_employment_description'] == sub_self_employment]

        elif sub_self_employment == None:
           filtered_df = filtered_df[(filtered_df['sub_self_employment_description'].isnull())]

        # if disaggregation_level is not None or disaggregation_level=="Broad status in employment":
        #     filtered_df = filtered_df[filtered_df['disaggregation_level_description'] == disaggregation_level]
        # elif disaggregation_level == None:
        #     filtered_df = filtered_df[(filtered_df['disaggregation_level_description'].isnull())]

        # if quarter is not None or quarter =="Jan-Mar":
        #     filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        # elif quarter == None:
        #     filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]

        
        # if hour_working is not None or hour_working =="All":
        #     filtered_df = filtered_df[filtered_df['hour_working_description'] == hour_working]
        # elif hour_working == None:
        #     filtered_df = filtered_df[(filtered_df['hour_working_description'].isnull())]
        

        #Add logic to remove rows in filtered_df dataframe that contains NULL Value for religion_description
        filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]
        filtered_df = filtered_df[(filtered_df['nic2_industry_description'].isnull())]
        filtered_df = filtered_df[(filtered_df['hour_working_description'].isnull())]
        filtered_df = filtered_df[(filtered_df['broad_employment_description'].isnull())]
        filtered_df=filtered_df[(filtered_df['nic_description'].isnull())]
        filtered_df = filtered_df[(filtered_df['social_group_description'].isnull())]
        filtered_df=filtered_df[(filtered_df['religion_description'].isnull())]

        
        
        # if sub_industry is not None or sub_industry =='05-09 (mining & quarrying)':
        # filtered_df = filtered_df[filtered_df['sub_industry_description'] == sub_industry]
        # elif sub_industry == None:
        #     filtered_df = filtered_df[(filtered_df['sub_industry_description'].isnull())]

        # if broad_employment is not None or broad_employment=="All":
        #     filtered_df = filtered_df[filtered_df['broad_employment_description'] == broad_employment]
        # elif broad_employment == None:
        #     filtered_df = filtered_df[(filtered_df['broad_employment_description'].isnull())]

        # if quarter is not None or quarter =="Jan-Mar":
        #     filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        # elif quarter == None:
        #     filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]

        # if sub_industry is not None or sub_industry =='05-09 (mining & quarrying)':
        #     filtered_df = filtered_df[filtered_df['sub_industry_description'] == sub_industry]
        # elif sub_industry == None:
        #     filtered_df = filtered_df[(filtered_df['sub_industry_description'].isnull())]
        
        # if hour_working is not None or hour_working =="All":
        #     filtered_df = filtered_df[filtered_df['hour_working_description'] == hour_working]
        # elif hour_working == None:
        #     filtered_df = filtered_df[(filtered_df['hour_working_description'].isnull())]
       

    elif indicator=="Average wage earnings (Rs.) per day from casual labour work":

        if disaggregation_level is not None or disaggregation_level=="Broad status in employment":
            filtered_df = filtered_df[filtered_df['disaggregation_level_description'] == disaggregation_level]
        elif disaggregation_level == None:
            filtered_df = filtered_df[(filtered_df['disaggregation_level_description'].isnull())]

    elif indicator=="Average no. of days worked in a week (0.0) for person with broad status in employment in CWS":

        if broad_employment is not None or broad_employment=="All":
            filtered_df = filtered_df[filtered_df['broad_employment_description'] == broad_employment]
        elif broad_employment == None:
            filtered_df = filtered_df[(filtered_df['broad_employment_description'].isnull())]

        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]
    
    elif indicator=='Average no. of days actually worked in a week (0.0) for person with broad status in employment in CWS':

        if broad_employment is not None or broad_employment=="All":
            filtered_df = filtered_df[filtered_df['broad_employment_description'] == broad_employment]
        elif broad_employment == None:
            filtered_df = filtered_df[(filtered_df['broad_employment_description'].isnull())]

        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]

    elif indicator=="Percentage  distribution of usually working persons":
          
        if work_industry is not None or work_industry =="Seconday":
            filtered_df = filtered_df[filtered_df['work_industry_description'] == work_industry]
        elif work_industry  == None:
            filtered_df = filtered_df[(filtered_df['work_industry_description'].isnull())]

    elif indicator=="Percentage distribution of  person working":
        if self_employment is not None or self_employment=="Self-Employed":
            filtered_df = filtered_df[filtered_df['self_employment_description'] == self_employment]

        elif self_employment == None:
           filtered_df = filtered_df[(filtered_df['self_employment_description'].isnull())]

        if sub_self_employment is not None or sub_self_employment=="Own account worker, employer":

            filtered_df = filtered_df[filtered_df['sub_self_employment_description'] == sub_self_employment]

        elif sub_self_employment == None:
           filtered_df = filtered_df[(filtered_df['sub_self_employment_description'].isnull())]

    elif indicator=="Average number of hours (0.0) actually worked per week considering all the economic activities performed during the week for person with broad status in employment in CWS":
        if broad_employment is not None or broad_employment=="All":
            filtered_df = filtered_df[filtered_df['broad_employment_description'] == broad_employment]
        elif broad_employment == None:
            filtered_df = filtered_df[(filtered_df['broad_employment_description'].isnull())]
        
        if quarter is not None or quarter =="Jan-Mar":
            filtered_df = filtered_df[filtered_df['quarter_description'] == quarter]
        elif quarter == None:
            filtered_df = filtered_df[(filtered_df['quarter_description'].isnull())]

        


    # if industry is not None or industry =="Agriculture, forestry and fishing":
    #     filtered_df = filtered_df[filtered_df['industry_description'] == industry]
       
    # elif industry == None:
    #     filtered_df = filtered_df[(filtered_df['industry_description'].isnull())]

    # if occupation_divisions is not None or occupation_divisions =="All":
    #     filtered_df = filtered_df[filtered_df['occupation_divisions_description'] == occupation_divisions]

    # elif occupation_divisions == None:
    #     filtered_df = filtered_df[(filtered_df['occupation_divisions_description'].isnull())]
     
    # if enterprise_type is not None or enterprise_type =="All":
    #     filtered_df = filtered_df[filtered_df['enterprise_type_description'] == enterprise_type]
    # elif enterprise_type == None:
    #     filtered_df = filtered_df[(filtered_df['enterprise_type_description'].isnull())]
    
    # if umpce is not None or umpce == "all":
    #     filtered_df = filtered_df[filtered_df['umpce_description'] == umpce]
    # elif umpce == None:
    #     filtered_df = filtered_df[(filtered_df['umpce_description'].isnull())] 

    
    # if disaggregation_level is not None or disaggregation_level=="Broad status in employment":
    # filtered_df = filtered_df[filtered_df['disaggregation_level_description'] == disaggregation_level]
    # elif disaggregation_level == None:
    #     filtered_df = filtered_df[(filtered_df['disaggregation_level_description'].isnull())]

    # if religion is not None or religion == 'Hinduism':
    #     filtered_df = filtered_df[filtered_df['religion_description'] == religion]
    # elif religion == None:
    #     filtered_df = filtered_df[(filtered_df['religion_description'].isnull())]  
    yaxis_title = indicator_df.loc[indicator_df["indicator_description"]==indicator , "indicator_display_description"].values[0]
    # Handle "Select All" in year dropdown
    if "Select All" in year:
        years = df["year"].unique()
       
    else:
        years = year
        
    filtered_df = filtered_df[filtered_df["year"].isin(years)]
    
    # Debug: Print filtered DataFrame
    print("Filtered DataFrame:\n", filtered_df[['year', 'indicator_value']])

    # If filtered DataFrame is empty, print a warning
    if filtered_df.empty:
        print("Warning: Filtered DataFrame is empty. Check filter criteria.")
    
    # Create the plot
    fig = go.Figure()
    if n_clicks > 0 or n_intervals == 1:
        fig.add_trace(go.Scatter(
            x=filtered_df["year"],
            y=filtered_df["indicator_value"],
            mode='lines+markers',
            marker=dict(size=12), 
            marker_color='#124365' 
            
        ))
        fig.update_layout(
            xaxis={"title": "Year"},
            yaxis={"title": yaxis_title},
            xaxis_title_font=dict(size=17, family='Arial, sans-serif', color='black', weight='bold'),
            yaxis_title_font=dict(size=17, family='Arial, sans-serif', color='black', weight='bold'),
            hovermode="closest",
            template='plotly_white',
            font_color='black',
            margin=dict(t=0),
            #  width=1370,
            #  height=661,
        )
        fig.update_xaxes(categoryorder='category ascending')
        fig.update_yaxes(categoryorder='category ascending')

    return fig

# Handle SVG download
@app.callback(
    Output("download", "data"),
    Input("download-svg-button", "n_clicks"),
    State("plot-output", "figure"),
    prevent_initial_call=True
)
def download_svg(n_clicks, figure):
    print('DOWNLOAD BUTTON CLICKED!')
    if n_clicks > 0:
        fig = go.Figure(figure)
        svg_str = pio.to_image(fig, format="svg")

        buffer = io.BytesIO()
        buffer.write(svg_str)
        buffer.seek(0)

        return dcc.send_bytes(buffer.getvalue(), "plot.svg")
    
# Run the app
if __name__ == '__main__':
    app.run_server(host ='localhost' ,debug=True,dev_tools_ui=False, dev_tools_props_check=False, port=4574)