import dash_mantine_components as dmc


def request_details():
    return dmc.Paper(
        [
            dmc.Text("Time Series for the requests made", size="lg", underline=True),
            dmc.Divider(color="orange", orientation="vertical"),
            dmc.Text(
                "Request vs Elapsed Time. Just to understand how much time it takes to fetch <= 1k animes from the "
                "MyAnimeList Server", style={"wordWrap": "break-word"})
        ], style={"backgroundColor": "orange"}
    )
