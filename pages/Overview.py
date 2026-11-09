import dash
from dash import dcc
import plotly.express as px
import pandas as pd
import dash_mantine_components as dmc


df = pd.read_csv('data/data_cleaned.csv')

# KPI measures

median_price  = df['Price'].median()

total_no_cars = df[df.columns[0]].count().astype(int)

pop_car_type,pop_car_type_np = df['BodyType'].value_counts().index[0], df['BodyType'].value_counts().iloc[0]

pop_car_brand,pop_car_brand_listings = (df['Brand'].value_counts().index[0],df['Brand'].value_counts().iloc[0])


# Price Distribution

price_limit = df["Price"].quantile(0.90)

df_filtered_for_price_dist = df[df["Price"] <= price_limit]


# Treemap df
brand_counts = df['Brand'].value_counts().reset_index()
brand_counts.columns = ['Brands', 'Counts']
brand_counts = brand_counts.head(15)

# State Average

median_price_state = (
    df.groupby('State')['Price']
    .median()
    .sort_values(ascending=False)
    .reset_index()
)

# Price vs Year

df_price_v_year = df[df["Price"] <= price_limit]


dash.register_page(__name__,path='/')



layout = dmc.MantineProvider(
    dmc.Container([
        dmc.Title("Overview",style = {"textAlign": "center"} ,c="blue" ,order=1),
        dmc.Space(h='xl'),
        dmc.SimpleGrid([
            dmc.Card(
                children=[
                    dmc.Stack(
                        children=[
                            dmc.Text(
                                "TOTAL CAR LISTED",
                                size="xs",
                                fw=700,
                                c="dimmed"
                            ),

                            dmc.Title(
                                f"{total_no_cars:,.0f}",
                                order=2
                            ),
                            dmc.Text(
                                "Total Number of Cars Listed",
                                size="sm",
                                c="dimmed"
                            )
                        ]
                    )
                ],
                withBorder=True,
                shadow="sm",
                radius="lg",
                p="lg"
            ),
            dmc.Card(
                children=[
                    dmc.Stack(
                        children=[
                            dmc.Text(
                                "MEDIAN CAR PRICE",
                                size="xs",
                                fw=700,
                                c="dimmed"
                            ),

                            dmc.Title(
                                f"${median_price:,.0f}",
                                order=2
                            ),
                            dmc.Text(
                                "Median price across all listings",
                                size="sm",
                                c="dimmed"
                            )
                        ]
                    )
                ],
                withBorder=True,
                shadow="sm",
                radius="lg",
                p="lg",
            ),
            dmc.Card(
                children=[
                    dmc.Stack(
                        children=[
                            dmc.Text(
                                "MOST POPULAR BRAND",
                                size="xs",
                                fw=700,
                                c="dimmed"
                            ),

                            dmc.Title(
                                f"{pop_car_brand}",
                                order=2
                            ),
                            dmc.Text(
                                f"{pop_car_brand_listings/total_no_cars*100:,.0f}% cars listed were a {pop_car_brand}",
                                size="sm",
                                c="dimmed"
                            )
                        ]
                    )
                ],
                withBorder=True,
                shadow="sm",
                radius="lg",
                p="lg",
            ),
            dmc.Card(
                children=[
                    dmc.Stack(
                        children=[
                            dmc.Text(
                                "MOST POPULAR CAR TYPE",
                                size="xs",
                                fw=700,
                                c="dimmed"
                            ),

                            dmc.Title(
                                f"{pop_car_type}",
                                order=2
                            ),
                            dmc.Text(
                                f"{pop_car_type_np/total_no_cars*100:,.0f}% of Cars listed were SUV",
                                size="sm",
                                c="dimmed"
                            )
                        ]
                    )
                ],
                withBorder=True,
                shadow="sm",
                radius="lg",
                p="lg",
            ),
        ], cols={"base": 2, "md": 4,"lg":4}),
        dmc.Space(h='xl'),
        dmc.SimpleGrid([
            dmc.Card(children = [dcc.Graph(figure=px.treemap(
                        brand_counts,
                        path=['Brands'],
                        values='Counts',
                        title='Vehicle Distribution by Brand'
                    ))],
             withBorder=True,
             shadow="sm",
             radius="sm",
             p="sm",
                 ),
            dmc.Card(children = [
                dcc.Graph(figure=px.bar(
                    median_price_state,
                    y='State',
                    x='Price',
                    title='Median Vehicle Price by State',
                    orientation = 'h',
                    labels={
                        'State': 'State',
                        'Price': 'Median Price (AUD)'
                    },
                    text_auto='$,.0f'
                ))],
             withBorder=True,
             shadow="sm",
             radius="sm",
             p="sm",
            ),
            dmc.Card(children = [dcc.Graph(figure=
                px.pie(
                        df,
                        names='Transmission',
                        title='Vehicle Distribution by Transmission Type',
                        hole = 0.5
                )
            )],
             withBorder=True,
             shadow="sm",
             radius="sm",
             p="sm",
            ),
            dmc.Card(children = [
                dcc.Graph(figure=px.histogram(
                    df_filtered_for_price_dist,
                    x = 'Price',
                    color='BodyType',
                    nbins = 50,
                    title="Distribution of Vehicle Prices",
                    labels={
                        "Price": "Vehicle Price (AUD)",
                        "count": "Number of Vehicles"
                    }).update_layout(
                    template="plotly_white",
                    bargap=0.05
                    ).update_xaxes(
                    tickprefix="$",
                    tickformat=","
                )),
            ],
            withBorder=True,
            shadow="sm",
            radius="sm",
            p="sm",
            ),
            dmc.Card(children = [
                dcc.Graph(figure=
                    px.bar(
                        df[df["BodyType"] != "Other"].groupby("BodyType")["Price"].median(),
                        y='Price',
                        labels = {
                            'Price': 'Median Price (AUD)',
                            'BodyType': 'Car Type',
                        }
                    )
                )
            ],
            withBorder=True,
            shadow="sm",
            radius="sm",
            p="sm"),
            dmc.Card(children = [
                dcc.Graph(figure=
                    px.scatter(
                        df_price_v_year,
                        x="Year",
                        y="Price",
                        color = 'BodyType',
                        # line_group="Brand",
                        # pattern_shape="Brand",
                        title="Vehicle Price by Manufacturing Year",
                        labels={
                            "Year": "Manufacturing Year",
                            "Price": "Vehicle Price (AUD)"
                        },

                    )
                )
            ],
            withBorder=True,
            shadow="sm",
            radius="sm",
            p="sm"),
        ], cols={"base": 1, "md": 2, "lg":3})
    ], fluid=True)
)