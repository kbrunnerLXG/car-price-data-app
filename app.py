import dash
from dash import Dash, Output, Input, State, ALL, callback_context
import dash_mantine_components as dmc


app = Dash(__name__, use_pages=True)
server = app.server


app.layout = dmc.MantineProvider(

    dmc.Container(
        [

            # Header
            dmc.Group(
                [
                    dmc.Button(
                        "☰ Menu",
                        id="open-drawer",
                        variant="light"
                    ),
                ],
                mb="md"
            ),


            # Navigation Drawer
            dmc.Drawer(
                title="Australian Vehicle Prices 2023",
                id="navigation-drawer",
                padding="md",
                size="250px",
                children=[
                    dmc.Stack(
                        [
                            dmc.NavLink(
                                label=page["name"],
                                href=page["relative_path"],
                                id={
                                    "type": "navlink",
                                    "index": page["relative_path"]
                                }
                            )
                            for page in dash.page_registry.values()
                        ]
                    )
                ]
            ),


            # Page content
            dmc.BackgroundImage(src = '',children =[dmc.Box(
                dash.page_container
            )])

        ],
        fluid=True,
        p="md"
    )
)


# Open and close the drawer
@app.callback(
    Output("navigation-drawer", "opened"),
    Input("open-drawer", "n_clicks"),
    State("navigation-drawer", "opened"),
    prevent_initial_call=True
)
def toggle_drawer(n_clicks, opened):
    return not opened


# Highlight active navigation link
@app.callback(
    Output({"type": "navlink", "index": ALL}, "active"),
    Input("_pages_location", "pathname")
)
def update_navlinks(pathname):

    return [
        control["id"]["index"] == pathname
        for control in callback_context.outputs_list
    ]


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080, use_reloader=False)