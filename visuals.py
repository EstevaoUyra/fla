import seaborn as sns
import matplotlib.pyplot as plt
from demoFunctions import getDemo


def stripDemog(demoData,field,proportion):
    '''Plot single chart with all data from the specified field'''
    fieldData = getDemo(demoData,field,proportion)
    fig = sns.stripplot(y='variable', x="value", hue="specifics",
                  data=fieldData, dodge=True, jitter=True,
                  alpha=.9, zorder=1)
    fig = plt.figure(1)
    plt.title(field)
    ax = fig.add_subplot(111)
    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(1.5,.6))
    ax.grid('on')

def plotResumed(demoData,field)
    pass
