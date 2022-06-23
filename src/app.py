import pandas as pd
import dash
import plotly.express as px  # (version 4.7.0 or higher)
from dash import dcc, html, Input, Output, dash_table  # pip install dash (version 2.0.0 or higher)
from flask import Flask
import helpers

server = Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(server=server, external_stylesheets=external_stylesheets)

# ------------------------------------------------------------------------------
# -- Import and clean csvs (importing csv into pandas)
# ------------------------------------------------------------------------------

df = pd.read_csv("./LuxuryLoanPortfolio.csv")

# Boxplot dataframe
df_boxplot = df.copy()
df_boxplot['funded_year'] = pd.DatetimeIndex(df_boxplot['funded_date']).year
df_boxplot['funded_month'] = pd.DatetimeIndex(df_boxplot['funded_date']).month
df_boxplot['ltv_ratio'] = round(df_boxplot['funded_amount'] / df_boxplot['property_value'],4)
df_boxplot = df_boxplot.loc[(df_boxplot["loan_id"] != "LL0000608")]

# Loan Amortization dataframe
df_loan = df.copy()

# NII dataframe
df_net_interest_income = pd.read_csv("./net_interest_income.csv")
df_net_interest_income = df_net_interest_income.groupby(["Year", "Purpose"])['Interest'].sum().reset_index()

# ------------------------------------------------------------------------------
# App layout
# ------------------------------------------------------------------------------

app.layout = html.Div(children=[
    html.Div([
        html.H1("Luxury Loan Portfolio Insights", style={'text-align': 'center'}),
        html.Br(),
        html.H4("1. Key Loan Metric Boxplots", style={'text-align': 'center'}),
        html.H5("Visualize the distribution of key metrics across selected dimensions", style={'text-align': 'center'}),
        html.Br(),
        html.P(" Metrics:", style={"padding-left": "10px"}),
        dcc.RadioItems(
            id='y-axis',
            options=[
                {'label': 'Loan-to-value Ratio', 'value': 'ltv_ratio'},
                {'label': 'Funded Amount', 'value': 'funded_amount'},
                {'label': 'Property Value', 'value': 'property_value'},
            ],
            value='ltv_ratio',
            inputStyle={"margin-left": "10px", "margin-right": "10px"}
        ),
        html.Br(),
        html.P("By:", style={"padding-left": "10px"}),
        dcc.RadioItems(
            id='x-axis',
            options=[
                {'label': 'Loan Purpose', 'value': 'purpose'},
                {'label': 'Funded Year', 'value': 'funded_year'},
                {'label': 'Tax Class at Present', 'value': 'tax_class_at_present'},
                {'label': 'Client Employment Length', 'value': 'employment_length'},
                {'label': 'Client Building Class Category', 'value': 'building_class_category'},
            ],
            value='funded_year',
            inputStyle={"margin-left": "10px","margin-right": "10px"}
         ),
        dcc.Graph(id="graph"),
        dcc.Markdown(
            '''
            ##### Observations
            - The median Loan-to-value Ratio has increased steadily from 0.86 in 2012 to 0.95 in 2019. 
            **This encourages risk-taking behaviour that might backfire for riskier asset classes e.g. investment property**   
            - The median Loan-to-value Ratio is the highest for plane-funding. 
            '''
        ),
    ], className='row'),
    html.Div([
        html.H4("2. Loan Amortization Schedule", style={'text-align': 'center'}),
        html.H5("See the annual loan amortization schedule for selected Loan ID", style={'text-align': 'center'}),
        html.Br(),
        html.P("Loan ID", style={"padding-left": "10px"}),
        dcc.Dropdown(
                    id="selected_loan_id",
                    options=df_loan.loan_id.unique(),
                    multi=False,
                    value="LL0000077",
                    style={'width': "40%", "padding-left": "10px"},
                    placeholder="Select a loan id",
                    ),
                html.Br(),
            dash_table.DataTable(
                id="dt1",
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white',
                     'textAlign': 'center'
                },
            ),
            dcc.Graph(id="graph2"),
    ], className='row'),
    html.Div([
            html.H4("3. Net Interest Income Schedule", style={'text-align': 'center'}),
            html.H5("Visualize the annual net interest income that the bank expects to earn from this portfolio", style={'text-align': 'center'}),
            dcc.Markdown(
                '''
                - Taking the 10 Year Treasury Index Fund Rate (10TIFR) as our cost of funds, we derive **Net Interest Margin = Loan Interest Rate - 10TIFR**. 
                - Thereafter, for each loan, we derive the amortization schedule and the associated net interest income 
                '''
            ),
            html.Br(),
            html.P("Loan Purpose", style={"padding-left": "10px"}),
            dcc.Checklist(
                id="selected_loan_purpose",
                options=df_loan.purpose.unique(),
                value=df_loan.purpose.unique(),
                style={'width': "40%", "padding-left": "10px"},
            ),
            dcc.Graph(id="graph3"),
            dcc.Markdown(
                        '''
                        ##### Observations
                        - Net interest income will peak in 2020 at just below $40 mn due to consistently strong loan book in previous years and long loan durations from property loans 
                        '''
                    ),
    ], className='row')
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# ------------------------------------------------------------------------------


@app.callback(
    Output("graph", "figure"),
    Output("graph2", "figure"),
    Output("dt1", "csvs"),
    Output("graph3", "figure"),
    Input("x-axis", "value"),
    Input("y-axis", "value"),
    Input("selected_loan_id", "value"),
    Input("selected_loan_purpose", "value"),
)
def generate_charts(x, y, loan_id, loan_purpose):
    # 1. Box Plot
    fig1 = px.box(df_boxplot, x=x, y=y, notched=True, points="all")

    # 2.1. Loan Amortization Schedule
    print(f"loan_id: {loan_id}")
    loan_interest_rate = df_loan.loc[df_loan.loan_id == loan_id, 'interest_rate'].values[0]
    loan_years = df_loan.loc[df_loan.loan_id == loan_id, 'duration_years'].values[0]
    loan_principal = df_loan.loc[df_loan.loan_id == loan_id, 'funded_amount'].values[0]
    loan_start_date = df_loan.loc[df_loan.loan_id == loan_id, 'funded_date'].values[0]
    print(f"loan_interest_rate: {loan_interest_rate}")
    print(f"loan_years: {loan_years}")
    print(f"loan_principal: {loan_principal}")
    print(f"loan_start_date: {loan_start_date}")
    print("-----------------")

    schedule, stats = helpers.get_amortization_table(loan_interest_rate, loan_years, 12, loan_principal, addl_principal=0, start_date=loan_start_date)
    annual_schedule = helpers.get_annual_payment_df(schedule)

    fig2 = px.bar(
        annual_schedule,
        x="Year",
        y=["Interest","Principal"],
        labels={"value": "Annual Payment", "variable": "Payment Type"}
    )
    fig2.update_traces(texttemplate="%{y:$,.0f}")

    # 2.2. Loan Statistics
    df_loan_stats = df_loan.loc[df_loan.loan_id == loan_id, ['firstname', 'lastname', 'phone', 'title', 'purpose', 'funded_date', 'funded_amount', 'duration_years', 'interest_rate', ]]
    df_loan_stats = df_loan_stats.to_dict('records')
    # print(df_loan_stats)

    # 3. Net Interest Income
    df_net_interest_income_final = df_net_interest_income[df_net_interest_income["Purpose"].isin(loan_purpose)]
    fig3 = px.area(df_net_interest_income_final,
                   x="Year",
                   y="Interest",
                   color="Purpose"
                   )
    fig3.update_traces(texttemplate="%{y:$,.0f}")

    return fig1, fig2, df_loan_stats, fig3


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=5000, debug=True)
    # src.run_server(debug=True)

