import dash
from dash import Output, Input, callback, dcc
import plotly.express as px
import dash_mantine_components as dmc
import pandas as pd
import numpy as np


dash.register_page(__name__)

df = pd.read_csv('data/data_cleaned.csv')


layout = dmc.MantineProvider(
    dmc.Container([
        dmc.Select(
                    label="Select a State",
                    id="state-select_dropdown",
                    data=[
                        {"value": "WA", "label": "Western Australia"},
                        {"value": "NSW", "label": "New South Wales"},
                        {"value": "VIC", "label": "Victoria"},
                        {"value": "TAS", "label": "Tasmania"},
                        {"value": "SA", "label": "South Australia"},
                        {"value": "NT", "label": "Northern Territory"},
                    ],
                    w=200,
                    mb=10,
                ),
        dmc.Title('State Specific Analysis', ta='center' ,c="blue" ,order=1),
        dmc.Space(h='xl'),
        dmc.SimpleGrid(children = [],cols={"base": 2, "md": 3,"lg":4} ,id = 'kpi_output'),
        dmc.Space(h='xl'),
        dmc.SimpleGrid(children = [], cols = {"base": 2, "md": 3} ,id = 'figure_output'),
    ],fluid=True,id="state-dashboard"),
)

@callback(
    Output("kpi_output", "children"),
    Output("figure_output", "children"),
    Input("state-select_dropdown", "value")
)
def update_dashboard(state):

    if state is None:
        return [], []


    filtered_df = df.loc[df["State"] == state, :]

    # KPI
    kpi_cards = kpi_gen(filtered_df)
    # Plot Figures
    figure_cards = figure_gen(filtered_df)

    return kpi_cards, figure_cards

def kpi_gen(filtered_df):

    total_records = len(filtered_df)
    average_price = filtered_df["Price"].mean()
    median_price = filtered_df["Price"].median()
    pop_car_brand,pop_car_brand_listings = (filtered_df['Brand'].value_counts().index[0],filtered_df['Brand'].value_counts().iloc[0])


    return [
        # KPI Card 1
        dmc.Card(
            children=[
                dmc.Stack(
                    children=[
                        dmc.Text("TOTAL CARS LISTED", size="xs", fw=700, c="dimmed"),
                        dmc.Title(f"{total_records:,.0f}", order=2),
                        dmc.Text("Total Number of Cars Listed", size="sm", c="dimmed")
                    ]
                )
            ],
            withBorder=True,
            shadow="sm",
            radius="lg",
            p="lg"
        ),

        # KPI Card 2
        dmc.Card(
            children=[
                dmc.Stack(
                    children=[
                        dmc.Text("AVERAGE PRICE", size="xs", fw=700, c="dimmed"),
                        dmc.Title(f"${average_price:,.0f}", order=2),
                        dmc.Text("Average Vehicle Price", size="sm", c="dimmed")
                    ]
                )
            ],
            withBorder=True,
            shadow="sm",
            radius="lg",
            p="lg"
        ),
        # KPI Card 3
        dmc.Card(
            children=[
                dmc.Stack(
                    children=[
                        dmc.Text("MEDIAN PRICE", size="xs", fw=700, c="dimmed"),
                        dmc.Title(f"${median_price:,.0f}", order=2),
                        dmc.Text("Median Vehicle Price", size="sm", c="dimmed")
                    ]
                )
            ],
            withBorder=True,
            shadow="sm",
            radius="lg",
            p="lg"
        ),
        # KPI Card 4
        dmc.Card(
            children=[
                dmc.Stack(
                    children=[
                        dmc.Text("POPULAR BRAND", size="xs", fw=700, c="dimmed"),
                        dmc.Title(f"{pop_car_brand}", order=2),
                        dmc.Text(f"{pop_car_brand} had {pop_car_brand_listings} listings", size="sm", c="dimmed")
                    ]
                )
            ],
            withBorder=True,
            shadow="sm",
            radius="lg",
            p="lg"
        )


    ]
def figure_gen(filtered_df):
    # total_records = len(filtered_df)
    price_limit = filtered_df["Price"].quantile(0.90)

    # dataframes
    ## grouped by year for price
    avg_price_by_year = filtered_df.groupby("Year")["Price"].mean().reset_index()
    avg_price_by_year = avg_price_by_year[avg_price_by_year["Price"] <= price_limit]

    ## grouped by brands and DriveType agg on count of listings
    brand_count = filtered_df.groupby(['Brand', 'DriveType']).size().reset_index(name='Count').sort_values('Count',
                                                                                                    ascending=False).head(
        15)

    ## Fuel Type Count
    fueltype_count = filtered_df['FuelType'].value_counts().reset_index()
    fueltype_count = fueltype_count[fueltype_count['FuelType'] != '-']
    fueltype_count = fueltype_count[fueltype_count['FuelType'] != 'Other']

    # Kilometres fix & Bucketing
    filtered_df = filtered_df[
        (filtered_df['Kilometres'] != '-') &
        (filtered_df['Kilometres'].notna())
        ].copy()
    filtered_df.loc[:, 'Kilometres'] = filtered_df['Kilometres'].astype(int)

    km_bins = [0, 50000, 100000, 150000, np.inf]
    km_names = ['0-50k', '50k-100k', '100k-150k', '150k+']

    filtered_df.loc[:, 'KMRange'] = pd.cut(
        filtered_df['Kilometres'],
        bins=km_bins,
        labels=km_names
    )

    # Year bucketing

    year_bins = [0, 2000, 2005, 2010, 2015, 2020, 2025, float('inf')]

    year_names = [
        'Before 2000',
        '2000–2004',
        '2005–2009',
        '2010–2014',
        '2015–2019',
        '2020–2024',
        '2025+'
    ]
    filtered_df.loc[:, 'YearRange'] = pd.cut(
        filtered_df['Year'],
        bins=year_bins,
        labels=year_names
    )


    # Heatmap Data
    heatmap_data = filtered_df.groupby(
        ['YearRange', 'KMRange'],
        observed=True
    )['Price'].median().reset_index()

    heatmap_matrix = heatmap_data.pivot(
        index='YearRange',
        columns='KMRange',
        values='Price'
    )

    return [
        dmc.Card(children=[dcc.Graph(figure=px.scatter(
            avg_price_by_year,
            x="Year",
            y='Price',
        ))],
            withBorder=True,
            shadow="sm",
            radius="sm",
            p="sm",
        ),
        dmc.Card(children=[
            dcc.Graph(figure=px.bar(
                brand_count,
                y = 'Brand',
                x = 'Count',
                color = 'DriveType',
                orientation = 'h',
            ).update_yaxes(
                tickmode='linear',
                dtick=1,
                categoryorder = 'total ascending'
            ))],
            withBorder=True,
            shadow="sm",
            radius="sm",
            p="sm",
        ),
        dmc.Card(children=
        [
            dcc.Graph(figure=px.box(
                filtered_df[
                    (filtered_df['Price'] < price_limit) & (filtered_df['FuelType'] != '-')
                ],
                y = 'Price',
                x = 'FuelType',
                )),
        ],
            withBorder=True,
            shadow="sm",
            radius="lg",
            p="sm",
        ),
        dmc.Card(children=[
            dcc.Graph(figure=
            px.box(filtered_df[filtered_df['Price'] < price_limit],
                   x = 'Transmission',
                   y = 'Price',))
        ],
            withBorder=True,
            shadow="sm",
            radius="sm",
            p="sm",
        ),
        dmc.Card(children=[
            dcc.Graph(
                figure=
                px.imshow(
                    heatmap_matrix,
                    labels={
                        'x': 'Kilometre Range',
                        'y': 'Manufacturing Year Range',
                        'color': 'Median Vehicle Price ($)'
                    },
                    title='Median Vehicle Price by Manufacturing Year and Kilometre Range',
                    aspect='auto'
                ),)
        ],
            withBorder=True,
            shadow="sm",
            radius="sm",
            p = "sm")

    ]

