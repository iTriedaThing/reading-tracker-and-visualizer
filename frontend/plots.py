import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class HorizontalBarGraph:
    def __init__(self):
        pass

    @staticmethod
    def plot_reading_progress(df: pd.DataFrame):
        # mark that a book was read on a given date
        df['read'] = 1
        pivot_df = df.pivot_table(index='date', columns='title', values='read', fill_value=0)

        # create a binary heatmap-style horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, len(pivot_df)))

        # plot the data
        cax = ax.matshow(pivot_df.T, cmap='Blues')

        # convert the index to a list of strings formatted as 'YYYY-MM-DD'
        formatted_dates = [date.strftime('%Y-%m-%d') for date in pivot_df.index]

        # set the axis labels
        ax.set_xticks(range(len(pivot_df.index)))
        ax.set_xticklabels(formatted_dates, rotation=90)
        ax.set_yticks(range(len(pivot_df.columns)))
        ax.set_yticklabels(pivot_df.columns)

        # set labels
        plt.xlabel('Date')
        plt.ylabel('Book Title')
        plt.title('Reading Progress by Date')

        # add aa color bar to explain the colors
        plt.colorbar(cax, ax=ax, orientation='vertical', label='Read (1=Yes, 0=No)')

        return fig
