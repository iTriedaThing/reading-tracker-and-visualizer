import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class HorizontalBarGraph:
    def __init__(self):
        pass

    @staticmethod
    def plot_reading_progress(df: pd.DataFrame, colormap:str):
        if not colormap:
            colormap = 'Blues'

        # mark that a book was read on a given date
        df['read'] = 1
        pivot_df = df.pivot_table(index='Date', columns='Title', values='read', fill_value=0)

        # create a binary heatmap-style horizontal bar chart
        fig, ax = plt.subplots(figsize=(len(pivot_df.columns), len(pivot_df)))

        # plot the data
        cax = ax.matshow(pivot_df, cmap=colormap)

        # convert the index to a list of strings formatted as 'YYYY-MM-DD'
        formatted_dates = [date.strftime('%Y-%m-%d') for date in pivot_df.index]

        # set the axis labels
        ax.set_xticks(range(len(pivot_df.columns)))
        ax.set_xticklabels(pivot_df.columns, rotation=90)
        ax.set_yticks(range(len(pivot_df.index)))
        ax.set_yticklabels(formatted_dates)

        # set labels
        plt.xlabel('Book Title')
        plt.ylabel('Date')
        plt.title('Reading Progress by Date')

        # add a color bar to explain the colors
        # plt.colorbar(cax, ax=ax, orientation='vertical', label='Read (1=Yes, 0=No)')

        return fig
