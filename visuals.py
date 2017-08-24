import seaborn as sns
import matplotlib.pyplot as plt
from demoFunctions import getDemo

# Plot simple chart with data from one field
def stripDemog(demoData,field):
    fieldData = getDemo(demoData,field,proportion=True)
    fig = sns.stripplot(y='variable', x="value", hue="specifics",
                  data=fieldData, dodge=True, jitter=True,
                  alpha=.9, zorder=1)
    fig = plt.figure(1)
    plt.title(field)
    ax = fig.add_subplot(111)
    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(1.5,.6))
    ax.grid('on')
