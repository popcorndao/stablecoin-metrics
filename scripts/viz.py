from matplotlib import pyplot as plt

def createBasicAnalysisPlot(df, fontsize = 16, ticksize = 12, title='DAI to USD', ylabel=None, price_dev=0.2):

    if ylabel is None:
        ylabel = title

    fig, axes = plt.subplots(nrows=2,ncols=1,sharex=True)
    fig.set_figwidth(18)
    fig.set_figheight(12)

    secax = [None] * 2

    axes[0].plot(df["date"], df["price"], color='black', linestyle='solid')
    axes[0].set_xlim([df.date.min(),df.date.max()])
    axes[0].set_facecolor((0.95, 0.95, 0.95))
    axes[0].set(ylim=[1 - price_dev, 1 + price_dev],
                ylabel=ylabel,
                title=title)
    axes[0].yaxis.label.set_fontsize(fontsize) 
    axes[0].title.set_fontsize(fontsize) 
    axes[0].tick_params(axis='both', which='major', labelsize=ticksize)
    axes[0].grid()

    axes[1].plot(df["date"], df["rate"], '-r')
    axes[1].fill_between(df["date"],
                         df["rate"] + df["rate_error"], 
                         df["rate"] - df["rate_error"],
                         color='red', alpha=.4)
    axes[1].set(ylim=[0, 0.25],
                ylabel='reversion rate to peg [$h^{-1}$]',
                xlabel='time',)
    axes[1].yaxis.label.set_color('red')
    axes[1].yaxis.label.set_fontsize(fontsize) 
    axes[1].xaxis.label.set_fontsize(fontsize) 
    axes[1].set_facecolor((0.95, 0.95, 0.95))
    axes[1].legend(labels=["reversion rate"], loc=(0.005, 0.925))

    axes[1].tick_params(axis='both', which='major', labelsize=ticksize)

    secax[1] = axes[1].twinx()
    secax[1].plot(df["date"], df["sigma"], '-g')
    secax[1].fill_between(df["date"],
                          df["sigma"] + df["sigma_error"], 
                          df["sigma"] - df["sigma_error"],
                          color='green', alpha=.4)
    secax[1].set(ylim=[0, 0.005], ylabel='sigma')
    secax[1].yaxis.label.set_color('green')
    secax[1].yaxis.label.set_fontsize(fontsize)
    secax[1].legend(labels=["sigma"], loc=(0.005, 0.85))
    secax[1].tick_params(axis='both', which='major', labelsize=ticksize)
    axes[1].grid()
    
    return fig, axes, secax