#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
gpoisson.py - GeigerLog commands for poisson statistics

include in programs with:
    import gpoisson
"""

###############################################################################
#    This file is part of GeigerLog.
#
#    GeigerLog is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GeigerLog is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GeigerLog.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = [""]
__license__         = "GPL3"


from   gutils            import *


#** Begin  newplotPoisson *****************************************************
def newplotPoisson():
    """Plotting a Poisson Fit to a histogram of the data"""

    vindex      = gglobs.exgg.select.currentIndex()
    vname       = gglobs.varnames[vindex]
    vnameFull   = gglobs.vardict[vname][0]

    if gglobs.logTimeDiffSlice is None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    try:
        t0 = gglobs.logTimeDiffSlice
        x0 = gglobs.logSliceMod[vname]
    except:
        gglobs.exgg.showStatusMessage("No data available")
        return
    #print("t0, x0: len:", len(t0), len(x0))

    gglobs.exgg.setBusyCursor()

    fncname = "newplotPoisson: "
    vprint(fncname + "Plotting Histogram and Poisson Fit")
    setDebugIndent(1)

    # elimitate all nan data in x (t will always exist)
    counter_isnan = 0
    t = np.ndarray(0)
    x = np.ndarray(0)
    for i in range(0,len(t0)):
        #print("i, x0[i]:", i, x0[i])
        if np.isnan(x0[i]):
            counter_isnan += 1
            pass

        else:
            t = np.append(t, t0[i])
            x = np.append(x, x0[i])
    #print("len(t0), len(x0), len(t), len(x): ", len(t0), len(x0), len(t), len(x))
    #if counter_isnan > 0:   print("Found nan, count:", counter_isnan)
    #else:                   print("Found no nan")

    DataSrc     = os.path.basename(gglobs.currentDBPath)
    cycletime   = (t[-1] - t[0]) / (t.size - 1)  # in minutes
    yunit       = vnameFull

    ######################################
    # to show histogram of delta between 2 consecutive counts
    if 0:       # do not execute on 0
        dx = x[:-1].copy()
        for i in range(0, len(dx)):
            dx[i] = abs(x[i+1] - x[i])
            #if dx[i] > 10: print i, dx[i]
        #print x, len(x)
        #print dx, len(dx)
        x = dx
        yunit = "Differences between 2 consecutive CPM!"
    #######################################


    lenx        = len(x)
    sumx        = np.nansum (x)         # nan...: all values excluding NANs!
    avgx        = np.nanmean(x)         # though there shouldn't be any, as they
    varx        = np.nanvar (x)         # are eliminated above
    stdx        = np.nanstd (x)         # But it does not hurt
    minx        = np.nanmin (x)
    maxx        = np.nanmax (x)
    std95       = np.sqrt(avgx) * 1.96  # +/- std95 is range for 95% of all values

    if avgx == 0:
        gglobs.exgg.showStatusMessage("All Variable data are zero; cannot calculate Poisson distribution!")
        setDebugIndent(0)
        gglobs.exgg.setNormalCursor()
        return


    wprint(fncname + "count data: lenx:{}, sumx:{:5.0f}, avgx:{:5.3f}, varx:{:5.3f}, stdx:{:5.3f}, minx:{:5.3f}, maxx:{:5.3f}, std95%:{:5.3f}\n{}\n".\
                format(lenx,   sumx,         avgx,          varx,         stdx,         minx,         maxx,         std95,           x))

    # take the lower of (the lowest count rate) and (the average minus 2 StdDev), but must be at least zero
    bin_center_min    = int(max(0,    min(minx , avgx - (std95 * 2))))

    # take the higher of (the highest count rate) and (the average plus 2 StdDev) and 16
    bin_center_max    = int(max(16, maxx , avgx + (std95 * 2)))

    # limit the total no of bins to 30 by making the bins wider, but keep width at least at 1
    step              = int(max(1, int((bin_center_max - bin_center_min) / 30)))
    bin_total         = int((bin_center_max - bin_center_min) / step) + 1
    #print("  step: {}, bin_center_min: {}, bin_center_max: {}, bin_total: {}".format(step, bin_center_min, bin_center_max, bin_total))

    bins    = np.empty(bin_total + 1)
    bins[0] = int(bin_center_min)
    for i in range(1, bin_total + 1):
        bins[i] = int(bins[i - 1] + step)
    #print("bins: len(): ", len(bins), bins)


    # CREATE histogram
    # https://numpy.org/devdocs/reference/generated/numpy.histogram.html
    # If bins is an int, it defines the number of equal-width bins in the given
    # range (10, by default).If bins is a sequence, it defines the bin edges,
    # including the rightmost edge, allowing for non-uniform bin widths.
    # If bins is a string, it defines the method used to calculate the optimal
    # bin width, as defined by histogram_bins.
    # hist, bins = np.histogram(x, bins='auto') # gives bins as rational numbers
    # hist, bins = np.histogram(x, bins='sqrt') # used in Excel; bins as rational numbers
    #
    # returns: The values of the histogram. See density and weights for a
    #          description of the possible semantics.
    #          bins : array of dtype float. Return the bin edges (length(hist)+1).

    # Here using manually created histogram, as otherwise a synthetic normal distribution
    # would not properly sum up
    hist = np.empty( len(bins) - 1 )
    for i in range(0, len(bins) - 1):
        stepsum = 0
        ll0 = bins[i ]
        hl0 = bins[i + 1]
        dl0 = hl0 - ll0
        for j in range(0, step):
            ll = ll0 - (dl0 / 2 / step) + dl0 /step * j
            hl = ll + dl0 / step
            stepsum += len( x[((x>=ll) & (x<hl))] )
            #print("i, j, ll0, hl0,  ll, hl, stepsum: ", i, j, ll0, hl0, ll, hl, stepsum)
        hist[i] = stepsum
    #print( "manual histogram: len(hist):", len(hist), "\n", hist)



    # sum up the Poisson dist for the bins from above histogram
    pdfs = []
    for i in range(int(bins[0]), int(bins[-1]), int(step)):
        stepsum = 0
        for j in range(0, step):
            stepsum += scipy.stats.poisson.pmf(i + j, avgx)
        pdfs.append(stepsum * lenx)

    #print("----------------avgx = ", avgx)
    pdfnorm = []
    for i in range(int(bins[0]), int(bins[-1]), int(step)):
        stepsum = 0
        for j in range(0, step):
            stepsum += scipy.stats.norm.pdf(i + j , avgx, scale=np.sqrt(avgx))
        pdfnorm.append(stepsum * lenx)

    # determine r-squared for Poisson
    ss_res = np.sum((hist - pdfs    ) ** 2)         # residual sum of squares
    ss_tot = np.sum((hist - np.mean(hist)) ** 2)    # total sum of squares
    r2 = 1 - (ss_res / ss_tot)                      # r-squared for poisson

    # determine r-squared for Normal
    ss_res = np.sum((hist - pdfnorm    ) ** 2)      # residual sum of squares
    ss_tot = np.sum((hist - np.mean(hist)) ** 2)    # total sum of squares
    r2N = 1 - (ss_res / ss_tot)                     # r-squared for normal



# chi squared stuff  ----------------------------------------------------------
    obs     = hist
    exp     = pdfs
    mini    = 0
    maxi    = len(obs)

    # find where obs and exp are both > 5
    # first the left side
    for i in range(len(obs)):
        #print("Left:   i={}, obs={:9.0f}, exp={:9.2f}".format(i, obs[i], exp[i] ))
        if obs[i] >=5 and exp[i] >= 5:
            #print("mini--> i={}, obs= {}, exp={}".format(i, obs[i], exp[i]))
            mini = i
            break

    # now the right side
    for i in range(mini, len(obs) ):
        #print("Right: i={}, obs={:9.0f}, exp={:9.2f}".format(i, obs[i], exp[i] ))
        if obs[i] <= 5 or exp[i] <= 5:
            #print("maxi--> i={}, obs= {}, exp={}".format(i, obs[i], exp[i]))
            maxi = i
            break

    # the ignored values on the right side
    for i in range(maxi, len(obs) ):
        pass
        #print("Rest:  i={}, obs={:9.0f}, exp={:9.2f}".format(i, obs[i], exp[i] ))

    wprint(fncname + "mini:{}, maxi:{}, diff:{}".format(mini, maxi, maxi - mini))



# calc chi2 manually
    #obs_mima = obs[mini:maxi] # cut out the part where obs and exp are both > 5
    #exp_mima = exp[mini:maxi]
    #
    #sumchi2 = 0
    #for i in range(0, len(obs_mima)):
    #    v = (obs_mima[i] - exp_mima[i])**2/exp_mima[i]
    #    sumchi2 += v
    #    print("i={:4d}, obs={:11.4f}, exp={:11.4f}, obs-exp={:11.4f}, chi2={:11.4f}, sumchi2={:11.4f}".format(i, obs_mima[i], exp_mima[i], obs_mima[i] - exp_mima[i], v, sumchi2))

#testing full Hist, not selected for > 5
    # calc chi2 for Poisson
    #ddofPoiss               = 1
    #dofPoiss                = len(hist) - ddofPoiss
    #chi2Poiss, pchi2Poiss   = scipy.stats.chisquare(hist, f_exp=pdfs,    ddof=ddofPoiss, axis=None)
    #txtChi2Poiss            = "Chi-squared Test Poisson <5:  DoF= {:1d}, chi² = {:5.1f}, p0= {:2.1%}".format(dofPoiss, chi2Poiss, pchi2Poiss)
    #vprint(fncname + txtChi2Poiss)


    # Degrees of Freedom
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html
    #   "ddofint, optional:
    #   Delta degrees of freedom”: adjustment to the degrees of freedom for the
    #   p-value. The p-value is computed using a chi-squared distribution with
    #   k - 1 - ddof degrees of freedom, where k is the number of observed
    #   frequencies. The default value of ddof is 0."
    #
    # assumption: for Poisson take 1 extra dof off ddof= 1 (estimate average from data)
    #             for Normal  take 2 extra dof off ddof= 2 (estimate average + StdDev from data)
    #
    # calc chi2 for Poisson
    ddofPoiss               = 1
    dofPoiss                = len(hist[mini:maxi]) - ddofPoiss
    chi2Poiss, pchi2Poiss   = scipy.stats.chisquare(hist[mini:maxi], f_exp=pdfs[mini:maxi],    ddof=ddofPoiss, axis=None)
    # testing same fucntion gives p=100%
    #chi2Poiss, pchi2Poiss   = scipy.stats.chisquare(pdfs[mini:maxi], f_exp=pdfs[mini:maxi],    ddof=ddofPoiss, axis=None)
    txtChi2Poiss            = "Chi-squared Test Poisson:  DoF = {:1d}, chi² = {:5.1f}, p = {:2.1%}".format(dofPoiss, chi2Poiss, pchi2Poiss)
    vprint(fncname + txtChi2Poiss)

    # calc chi2 for Normal
    ddofNorm                = 2
    dofNorm                 = len(hist[mini:maxi]) - ddofNorm
    chi2Norm, pchi2Norm     = scipy.stats.chisquare(hist[mini:maxi], f_exp=pdfnorm[mini:maxi], ddof=ddofNorm, axis=None)
    # testing same fucntion gives p=100%
    #chi2Norm, pchi2Norm     = scipy.stats.chisquare(pdfnorm[mini:maxi], f_exp=pdfnorm[mini:maxi], ddof=ddofNorm, axis=None)
    txtChi2Norm             = "Chi-squared Test Normal :  DoF = {:1d}, chi² = {:5.1f}, p = {:2.1%}".format(dofNorm, chi2Norm, pchi2Norm)
    vprint(fncname + txtChi2Norm)

# END chi squared stuff  ------------------------------------------------------


# Kolmogorov-Smirnoff stuff ---------------------------------------------------
    #print("avgx: ", avgx)
    obs     = hist
    exp     = pdfs
    #print("blue values:\n", obs)
    #print("red  values:\n", exp)

    #print(scipy.stats.kstest(exp,'poisson', args=(20,), alternative='less'))

    ks_stats_p, ks_pval_p = scipy.stats.kstest(x, 'poisson', args=(avgx,))
    ks_stats_n, ks_pval_n = scipy.stats.kstest(x, 'norm'   , args=(avgx,))
    #print("========================= x_norm    : avg:", avgx, ks_stats_n, ks_pval_n)
    #print("========================= x_pois    : avg:", avgx, ks_stats_p, ks_pval_p)

    obs_cum  = np.empty_like(obs)
    exp_cum  = np.empty_like(exp)

    for i in range(0, len(obs) +1):
        obs_cum = np.cumsum(obs[0:i])
        exp_cum = np.cumsum(exp[0:i])

    #print("obs_cum: \n", obs_cum)
    #print("exp_cum: \n", exp_cum)

    #diff  = np.empty_like(obs)
    #for i in range(0, len(obs)):
    #    diff[i] = obs_cum[i] - exp_cum[i]
    #print("diff: \n", diff)
    #print("diff: \n", np.absolute(diff))

    #diffmax = np.max(np.absolute(diff))
    #print("diffmax: ", diffmax)

# END   Kolmogorov-Smirnoff stuff ---------------------------------------------------


    fig2 = plt.figure(facecolor = "#E7F9C9")
    vprint("newplotPoisson: open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))
    #~try:
        #~plt.clf()
        #~vprint("newplotPoisson: open figs: {},  did plt.clf() on fig #{}".format(len(plt.get_fignums()), plt.gcf().number))
        #~print("newplotPoisson: plt.get_fignums():", plt.get_fignums())

    #~except Exception as e:
        #~srcinfo = "newplotPoisson: plt.clf() failed"
        #~exceptPrint(e, sys.exc_info(), srcinfo)
        #~return


    plt.suptitle("Histogram with Poisson Fit", fontsize=12 )
    RsubTitle = DataSrc + "  Recs:" + str(x.size)
    plt.title(RsubTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel("Variable {}".format(yunit), fontsize=12)
    plt.ylabel("Frequency of Occurence", fontsize=12)
    plt.grid(True)
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.17, top=0.85, bottom=0.15, right=.97)
    plt.ticklabel_format(useOffset=False)

    # canvas - this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvas2 = FigureCanvas(fig2)
    canvas2.setFixedSize(600,400) # needs to be >=600 wide for the nav coords to show even when in 2 lines!


    # plot histogram and other curves #########################################

    # histogram
    plt.bar(bins[:-1],  hist,        color="cornflowerblue", align='center', width=step * 0.85,   label ="avg = {:0.2f}\nvar = {:0.2f}".format(avgx, varx))

    # Poisson curve
    plt.plot(bins[:-1], pdfs,        color='red',         linewidth=3,                        label ="r2  = {:0.3f}".format(r2))

    # Poisson curve residuals
    plt.plot(bins[:-1], hist - pdfs, color='orangered',   linewidth=1, marker='o', markersize=3, label="Residuals")

    if gglobs.stattest:
        # Normal curve
        plt.plot(bins[:-1], pdfnorm,        color='black', linewidth=1,                            label ="N r2 = {:0.3f}".format(r2N))

        # Normal curve residuals
        plt.plot(bins[:-1], hist - pdfnorm, color='0.3',   linewidth=1, marker='s', markersize=3,  label="N Residuals")

    # best place for Legend found with "best"!
    plt.legend(loc="best", fontsize=12, prop={"family":"monospace"})

    ###########################################################################

    labout  = QTextBrowser() # label to hold the description
    labout.setFont(gglobs.exgg.fontstd)
    labout.setLineWrapMode(QTextEdit.NoWrap)
    labout.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
    labout.setMinimumHeight(330)
    #labout.setMinimumHeight(550)

    labout.append("Bin   Count Rate    Frequency    % of   Poisson-Fit    Residuals")

    if step == 1:
        # bins have only 1 count rate
        labout.append("No.                (blue col)   Total    (red line) (Freq - Fit)")
        for i in range(0, len(hist)):
            labout.append("{:3d}   {:4.1f}           {:8.1f}  {:5.2f}%    {:10.1f}   {:+10.1f}".format(i + 1, bins[i], hist[i], hist[i]*100./lenx, pdfs[i], hist[i] - pdfs[i]))
    else:
        # bins have more than one count rate
        labout.append("No.   from ... to  (blue col)   Total    (red line) (Freq - Fit)")
        for i in range(0, len(hist)):
            labout.append("{:3d}   {:4.1f} ...{:4.1f}   {:8.1f}  {:5.2f}%    {:10.1f}   {:+10.1f}".format(i + 1, bins[i], bins[i+1] - 1, hist[i], hist[i]*100./lenx, pdfs[i], hist[i] - pdfs[i]))

    labout.append("Total count=       {:10.1f}  100.00%   {:10.1f}   {:+10.1f}".format(sum(hist), sum(pdfs), sum(hist - pdfs)))

    labout.append("Countrates per Bin: {}".format(step))

    labout.append("\nGoodness of Fit Poisson :  r²  = {:5.3f}".format(r2))
    labout.append(txtChi2Poiss)

    if gglobs.stattest:
        labout.append("Goodness of Fit Normal  :  r²  = {:5.3f}".format(r2N))
        labout.append(txtChi2Norm)

#    labout.append("Kolmogorov-Smirnow Poisson Test: ")
#    labout.append("Poisson :  statistic = {:5.3f}, pvalue= {:2.3%}".format(ks_stats_p, ks_pval_p))
#    labout.append("Normal  :  statistic = {:5.3f}, pvalue= {:2.3%}".format(ks_stats_n, ks_pval_n))


# Assemble Data set statistics
    labout.append("\nData Set:")
    labout.append("File      = {}"    .format(DataSrc))
    labout.append("Records   = {}"    .format(x.size))
    labout.append("Cycletime ={:8.2f}".format(cycletime * 86400) + " sec (overall average)")
    labout.append("Average   ={:8.2f}".format(avgx))
    labout.append("Variance  ={:8.2f}  same as Average if true Poisson Dist.".format(varx))
    labout.append("Std.Dev.  ={:8.2f}".format(stdx))
    labout.append("Sqrt(Avg) ={:8.2f}  same as Std.Dev. if true Poisson Dist.".format(np.sqrt(avgx)))
    labout.append("Std.Err.  ={:8.2f}".format(stdx / np.sqrt(x.size)))
    labout.append("Skewness  ={:8.2f}  0:Norm.Dist.; skewed to: +:right   -:left".format(scipy.stats.skew    (x) ))
    labout.append("Kurtosis  ={:8.2f}  0:Norm.Dist.; shape is:  +:pointy: -:flat".format(scipy.stats.kurtosis(x) ))
    labout.append("")


    d       = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setWindowTitle("Poisson Test")
    #d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    d.setWindowModality(Qt.WindowModal)

    #~mystatusBar = QStatusBar()
    #~mystatusBar.showMessage("")

    navtoolbar = NavigationToolbar(canvas2, d) # choice of parent does not matter?
    #~navtoolbar = NavigationToolbar(canvas2, None) # choice of parent does not matter?
    #~navtoolbar = NavigationToolbar(canvas2, gglobs.exgg) # choice of parent does not matter?

    # hide the cursor position from showing in the Nav toolbar
    #ax1 = plt.gca()
    #~ax1.format_coord = lambda x,y: f"x={x:.1f}, y={y:.1f}"
    #~ax1.format_coord = lambda x,y: "x={:.1f},\ny={:.1f}".format(x, y)
    #ax1.format_coord = lambda x,y: "x={:.1f}, y={:.1f}".format(x, y)

    bbox    = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: d.done(0))

    #~layoutHtb = QHBoxLayout()
 #~#   layoutHtb.addWidget(bbox)
    #~layoutHtb.addWidget(navtoolbar)
    #~layoutHtb.addStretch()
    #~layoutHtb.addStretch() # strange - one is not enough? on Py3.5
    #~layoutHtb.addStretch() # strange - one is not enough? on Py3.8

    layoutV   = QVBoxLayout(d)
    layoutV.addWidget(navtoolbar)
    #layoutV.addLayout(layoutHtb)
    layoutV.addWidget(canvas2)
    #~layoutV.addWidget(mystatusBar)
    layoutV.addWidget(labout)
    layoutV.addWidget(bbox)

    gglobs.exgg.setNormalCursor()

# show window
    fig2.canvas.draw_idle()
    d.exec()
    plt.close(fig2)
    setDebugIndent(0)

#** End  newplotPoisson *******************************************************


#** Begin  newplotFFT *********************************************************

def newplotFFT():
    """Plotting FFT and Autocorrelation"""

    # nomenclature
    # t       = time
    # sigt    = Signal in time domain, (like CPM/CPS)
    # freq    = Signal in frequency domain

    if gglobs.logTimeSlice is None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    vindex      = gglobs.exgg.select.currentIndex()
    vname       = gglobs.varnames[vindex]
    vnameFull   = gglobs.vardict[vname][0]
    yunit       = vnameFull
    #print("plotFFT: vname, vnameFull: ", vname, vnameFull)

    try:
        rawt0    = gglobs.logTimeDiffSlice
    except Exception as e:
        srcinfo = "plotFFT: could not load time data"
        exceptPrint(e, sys.exc_info(), srcinfo)
        return

    try:
        rawsigt0 = gglobs.logSliceMod[vname]
    except Exception as e:
        srcinfo = "plotFFT: could not load value data"
        exceptPrint(e, sys.exc_info(), srcinfo)
        return

    if rawsigt0 is None:
        #~self.showStatusMessage("No data available")
        gglobs.exgg.showStatusMessage("No data available")
        return

    if rawt0.size < 20:
        #~self.showStatusMessage("Not enough data (need 20+)")
        gglobs.exgg.showStatusMessage("Not enough data (need 20+)")
        return

    gglobs.exgg.setBusyCursor()

    #print("rawt0, rawsigt0: len:", len(rawt0), len(rawsigt0))
    rawt    = np.ndarray(0)
    rawsigt = np.ndarray(0)
    for i in range(0,len(rawt0)):
        if np.isnan(rawsigt0[i]):
            #print("i, x0[i]:", i, x0[i])
            continue
        else:
            #print("i, x[i]:", i, x0[i])
            rawt    = np.append(rawt,    rawt0[i])
            rawsigt = np.append(rawsigt, rawsigt0[i])
    #print("rawt, rawsigt: len:", len(rawt), len(rawsigt))

    markersize  = 1.0
    DataSrc     = os.path.basename(gglobs.currentDBPath)

    t    = rawt.copy()
    sigt = rawsigt.copy()


    ####### Window functions ##############################################
    # the only place to activate Window function is this:
    use_window_functions = False

    if use_window_functions:
    # the window functions:
        hamm    = np.hamming (len(t))
        hann    = np.hanning (len(t))
        black   = np.blackman(len(t))
        # Kaiser:
        # "A beta value of 14 is probably a good starting point"
        # beta  Window shape
        # 0     Rectangular
        # 5     Similar to a Hamming
        # 6     Similar to a Hanning
        # 8.6   Similar to a Blackman
        beta    = 5
        kaiser  = np.kaiser(len(t), beta)

    # Select one of the windows functions
        #win     = hamm
        #win     = hann
        #win     = black
        win     = kaiser

    # apply window function
        # When using window function subtract the average in order to avoid
        # spurious low-frequency peaks!
        sigt   = sigt - np.mean(sigt)
        #sigt2  = sigt - np.mean(sigt)

        # Time domain signal with Window function applied
        sigt_win = sigt * win
    #######################################################################

    t               = t * 1440.0  # convert days to minutes
    timeunit        = "minutes"
    frequencyunit   = "1/minute"
    cycletime       = (t[-1] - t[0]) / (t.size -1)  # in minutes

    # calc with ignoreing the nan values            # including nan values
    sigt_mean       = np.nanmean    (sigt)          # np.mean(sigt)
    sigt_var        = np.nanvar     (sigt)          # np.var(sigt)
    sigt_std        = np.nanstd     (sigt)          # np.std(sigt)
    sigt_err        = sigt_std / np.sqrt(sigt.size) # sigt_std / np.sqrt(sigt.size)


#testing
    #~print("----------------sigt_mean = ", sigt_mean)
    #~print("----------------sigt_var = ", sigt_var)
    #~print("----------------sigt_std = ", sigt_std)
    #~print("----------------sigt_err = ", sigt_err)


    if sigt_var == 0:
        gglobs.exgg.showStatusMessage("All data variances are zero; cannot calculate FFT!")
        setDebugIndent(0)
        gglobs.exgg.setNormalCursor()
        return



    # FFT calculation #####################################################
    # using amplitude spectrum, not power spectrum; power would be freq^2
    freq         = np.abs(np.fft.rfft(sigt     ))
    #freq2        = np.abs(np.fft.rfft(sigt2    ))

    if use_window_functions:
        freq_win     = np.abs(np.fft.rfft(sigt_win ))

    # Return the Discrete Fourier Transform sample frequencies
    f = np.fft.rfftfreq(t.size, d = cycletime)
    #print "f:   len:", f.size, "\n", f

    # Return the reciprocal of the argument, element-wise.
    p  = np.reciprocal(f[1:])  # skipping 1st value frequency = 0
    #print "Period: len:", p.size, "\n", p


    asigt = sigt - sigt_mean

    #print "np.mean(sigt) , np.var(sigt) :", np.mean(sigt),  np.var(sigt)
    #print "np.mean(asigt), np.var(asigt):", np.mean(asigt), np.var(asigt)

    asigtnorm = np.var(asigt) * asigt.size  # to normalize autocorrelation

    # Cross-correlation of two 1-dimensional sequences.

    ac = np.correlate(asigt, asigt, mode='full') / asigtnorm
    #print( "ac: len:", ac.size)
    ac = ac[int(ac.size/2):]
    #print( "ac: len:", ac.size)
    #print( "ac:", "\n", ac)


# figure and canvas ###################################################
    #~figFFT = plt.figure(3, facecolor = "#C9F9F0") # blueish tint
    figFFT = plt.figure(facecolor = "#C9F9F0") # blueish tint
    vprint("newplotFFT: open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))
    #~plt.clf()
    #~try:
        #~plt.clf()
        #~vprint("newplotFFT: Did plt.clf()")
    #~except Exception as e:
        #~srcinfo = "newplotFFT: plt.clf() failed"
        #~exceptPrint(e, sys.exc_info(), srcinfo)


    # canvas - this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvas3 = FigureCanvas(figFFT)
    canvas3.setFixedSize(1000, 600)
    navtoolbar = NavigationToolbar(canvas3, gglobs.exgg)


# Data vs Time ################################################################
    plt.subplot(2,2,1)
    plt.title("Time Course", fontsize=12, loc = 'left')
    subTitle = "Recs:" + str(sigt.size)
    plt.title(subTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel("Time ({})".format(timeunit), fontsize=12)
    plt.ylabel("Variable  " + yunit, fontsize=12)
    plt.grid(True)
    plt.ticklabel_format(useOffset=False)

    plt.plot(t, sigt        ,  linewidth=0.4, color='red'   , label ="Time Domain" , marker="o", markeredgecolor='red'   , markersize=markersize)
    #plt.plot(t, sigt_win    ,  linewidth=0.4, color='black' , label ="Time Domain" , marker="o", markeredgecolor='black' , markersize=markersize)


    #def format_coord(x, y):
    #    col = int(x + 0.5)
    #    row = int(y + 0.5)
    #    z = 99
    #    return 'aaaaaaaaaaaaaaaaaaa x=%1.4f, y=%1.4f, z=%1.4f' % (x, y, z)

    # hide the cursor position from showing in the Nav toolbar
    #ax1 = plt.gca()
    #ax1.format_coord = lambda x, y: "asasjalksjalsjalskajlakj"
    #ax1.format_coord = format_coord


# Autocorrelation vs Lag #########################################################
    aax1 =  plt.subplot(2,2,3)

    plt.title("Autocorrelation (normalized) vs. Lag Period", fontsize=12, loc = 'left', y = 1.1)
    plt.xlabel("Lag Period ({})".format(timeunit), fontsize=12)
    plt.ylabel("Autocorrelation", fontsize=12)
    plt.grid(True)
    #plt.ticklabel_format(useOffset=False)

    aax2 = aax1.twiny()

    # how many points to show enlarged?
    for i in range(t.size):
        if ac[i] < 0: break

    tindex = min(i, t.size * 0.01)
    tindex = max(25, tindex, 60./(cycletime * 60.))
    tindex = int(tindex)  # Warning: ./geigerlog:3483: VisibleDeprecationWarning: using a non-integer number instead of an integer will result in an error in the future
                          # aax2.plot(tnew[:tindex], ac[:tindex], linewidth= 2.0, color='blue' , label ="Expanded Lag Period - Top Scale" , marker="o", markeredgecolor='blue'  , markersize=markersize*2)
                          # What is the reason ?????
    #print "tindex:", tindex
    #print "type(tindex):", type(tindex)

    tnew = t - t[0]
    aax1.plot(tnew,          ac         , linewidth= 0.4, color='red'  , label ="Full Lag Period - Bottom Scale" , marker="o", markeredgecolor='red'   , markersize=markersize)
    #aax1.legend(loc='upper right', fontsize=12)

    aax2.plot(tnew[:tindex], ac[:tindex], linewidth= 2.0, color='blue' , label ="Expanded Lag Period - Top Scale" , marker="o", markeredgecolor='blue'  , markersize=markersize * 2)
    #print "ac:", ac[:10]

    plt.legend(loc='upper right', fontsize=10)

    for a in aax1.get_xticklabels():
        #a.set_color("red")
        #a.set_weight("bold")
        pass

    for a in aax2.get_xticklabels():
        a.set_color("blue")
#            a.set_weight("bold")



# FFT vs Time #########################################################
    plt.subplot(2,2,2)
    plt.title("FFT Amplitude Spectrum vs. Time Period", fontsize=12, loc = 'left')
    plt.xlabel("Time Period ({})".format(timeunit), fontsize=12)
    plt.ylabel("FFT Amplitude", fontsize=12)
    plt.grid(True)
    plt.ticklabel_format(useOffset=False)

    plt.loglog(p, freq[1:]        , linewidth= 0.4, color='red'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)
    #plt.loglog(p, freq2[1:] -freq[1:]       , linewidth= 0.4, color='black'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)
    #plt.loglog(p, freq_win[1:]    , linewidth= 0.4, color='black' , label ="FFT" , marker="o", markeredgecolor='black' , markersize=markersize)

# FFT vs Frequency ####################################################
    plt.subplot(2,2,4)
    plt.title("FFT Amplitude Spectrum vs. Frequency", fontsize=12, loc = 'left')
    plt.xlabel("Frequency ({})".format(frequencyunit), fontsize=12)
    plt.ylabel("FFT Amplitude", fontsize=12)
    plt.grid(True)
    plt.ticklabel_format(useOffset=False)

    plt.semilogy (f[1:], freq[1:]     , linewidth= 0.4, color='red'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)
    #plt.semilogy (f[1:], freq2[1:] -freq[1:]     , linewidth= 0.4, color='black'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)
    #plt.semilogy (f[1:], freq_win[1:] , linewidth= 0.4, color='black' , label ="FFT" , marker="o", markeredgecolor='black' , markersize=markersize)

    #plt.legend(loc='upper left', fontsize=12)

# arrange sub plots
    plt.subplots_adjust(hspace=0.5, wspace=0.2, left=.08, top=0.95, bottom=0.090, right=.98)

# textboxes ################################################################
    labout_left  = QTextBrowser() # label to hold some data on left side
    labout_left.setFont(gglobs.exgg.fontstd)
    labout_left.setLineWrapMode(QTextEdit.NoWrap)
    labout_left.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
    labout_left.setMinimumHeight(150)

    labout_left.append("{:22s}= {}"                             .format('File'               , DataSrc))
    labout_left.append("{:22s}= {}"                             .format("No of Records"      , t.size))
    labout_left.append("{:22s}= {:4.2f}"                        .format("Count Rate Average" , sigt_mean))
    labout_left.append("{:22s}= {:4.2f} (Std.Dev:{:5.2f}, Std.Err:{:5.2f})"    .format("Count Rate Variance" , sigt_var, sigt_std, sigt_err))
    labout_left.append("{:22s}= {:4.2f} sec (overall average)"  .format("Cycle Time"         , cycletime * 60.)) # t is in minutes
    labout_left.append("{:22s}= {:4.2f} "                       .format("A.corr(lag=  0   sec)", ac[0]))
    labout_left.append("{:22s}= {:4.2f} "                       .format("A.corr(lag={:5.1f} sec)".format(tnew[1] *60.), ac[1]))
    labout_left.append("{:22s}= {:4.2f} "                       .format("A.corr(lag={:5.1f} sec)".format(tnew[2] *60.), ac[2]))

    labout_right  = QTextBrowser() # label to hold some data on right side
    labout_right.setFont(gglobs.exgg.fontstd)
    labout_right.setLineWrapMode(QTextEdit.NoWrap)
    labout_right.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
    labout_right.setMinimumHeight(120)

    fftmax      = np.max    (freq[1:])
    fftmaxindex = np.argmax (freq[1:]) + 1
    f_max       = f         [fftmaxindex ]

    labout_right.append("{:22s}= {:4.0f}"              .format("FFT(f=0)"         , freq[0]) )
    labout_right.append("{:22s}= {:4.2f} (= FFT(f=0)/No of Records)".format("Count Rate Average", freq[0] / len(t)) )
    labout_right.append("{:22s}= {:4.2f}"              .format("Max FFT(f>0)"     , fftmax))
    labout_right.append("{:22s}= {}"                   .format("  @ Index"        , fftmaxindex))
    labout_right.append("{:22s}= {:4.4f}"              .format("  @ Frequency"    , f_max ))
    labout_right.append("{:22s}= {:4.4f}"              .format("  @ Period"       , p[fftmaxindex] ))

# Pop Up  #################################################################
    d       = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    #d.setFont(self.fontstd)
    #d.setWindowTitle("FFT & Autocorrelation" + winTitleLabel)
    d.setWindowTitle("FFT & Autocorrelation" )
    #d.setMinimumHeight(gglobs.window_height)
    #d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    d.setWindowModality(Qt.WindowModal)

    bbox    = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: d.done(0))

    layoutH   = QHBoxLayout()
    layoutH.addWidget(labout_left)
    layoutH.addWidget(labout_right)


    #~layoutHtb = QHBoxLayout()
    #~layoutHtb.addWidget(bbox)
    #~layoutHtb.addWidget(navtoolbar)
    #~layoutHtb.addStretch()
    #~layoutHtb.addStretch() # strange - one is not enough? on Py3.5
    #~layoutHtb.addStretch() # strange - one is not enough? on Py3.8
    #~layoutHtb.addStretch() # strange - one is not enough? on Py3.8
    #~layoutHtb.addStretch() # strange - one is not enough? on Py3.8


    layoutV   = QVBoxLayout(d)
    #layoutV.addLayout(layoutHtb)
    layoutV.addWidget(navtoolbar)
    layoutV.addWidget(canvas3)
    layoutV.addLayout(layoutH)
    layoutV.addWidget(bbox)

    gglobs.exgg.setNormalCursor()

    figFFT.canvas.draw_idle()
    d.exec()
    plt.close(figFFT)

#**End newplotFFT  ************************************************************



#**Begin Eval_plotFFT *********************************************************

def Eval_plotFFT(self, type = 'plot'):
    """Plotting FFT and Autocorrelation
    t       = time
    sigt    = Signal in time domain, (CPM/CPS here)
    freq    = Signal in frequency domain

    Has extra function for rectangle and autocorr
    """
    #
    # must be reworked. e.g. 'gglobs.focus' is no longer in use !!!
    #
    fprint("Eval_plotFFT is inactive", error=True)
    return

    markersize = 0.5#1.0

    if type == 'plot':              # use only data shown in the plot
        #print "gglobs.logTimeDiffSlice:", len(gglobs.logTimeDiffSlice), "\n", gglobs.logTimeDiffSlice
        #print "gglobs.logCPMSlice:", len(gglobs.logCPMSlice), "\n", gglobs.logCPMSlice
        rawt    = gglobs.logTimeDiffSlice
        if gglobs.focus == "Left":
            rawsigt = gglobs.logCPMSlice
            yunit = "CPM"
        else:
            rawsigt = gglobs.logCPSSlice
            yunit = "CPS"
        winTitleLabel = " (Data from Plot Only)"
    else:                           # use all data of the file
        #print "gglobs.logTimeDiff", len(), "\n", gglobs.logTimeDiff
        #print "gglobs.logCPM", len(gglobs.logCPM), "\n", gglobs.logCPM
        rawt    = gglobs.logTimeDiff
        if gglobs.focus == "Left":
            rawsigt = gglobs.logCPM
            yunit = "CPM"
        else:
            rawsigt = gglobs.logCPS
            yunit = "CPS"

        winTitleLabel = " (Data from complete File )"

    if rawsigt is None:
        self.showStatusMessage("No data available")
        return

    if rawt.size < 20:
        self.showStatusMessage("Not enough data (need 20+)")
        return

    DataSrc = os.path.basename(gglobs.currentDBPath)

    t    = rawt.copy()
    sigt = rawsigt.copy()



# Window functions ############################################################
    # the only place to activate Window function is here
    use_window_functions = False

    if use_window_functions:
        hamm    = np.hamming (len(t))
        hann    = np.hanning (len(t))
        black   = np.blackman(len(t))
        # Kaiser:
        # "A beta value of 14 is probably a good starting point"
        # beta  Window shape
        # 0     Rectangular
        # 5     Similar to a Hamming
        # 6     Similar to a Hanning
        # 8.6   Similar to a Blackman
        beta    = 5
        kaiser  = np.kaiser(len(t), beta)

        # Select one
        #win     = hamm
        #win     = hann
        #win     = black
        win     = kaiser

        # When using window functions subtract the average in order to avoid
        # spurious low-frequency peaks!
        sigt   = sigt - np.mean(sigt)

        # Time domain signal with Window function applied
        sigt_win = sigt * win

# Prepare variables ###########################################################

    t               = t * 1440.0  # convert days to minutes
    timeunit        = "minutes"
    frequencyunit   = "1/minute"
    cycletime       = (t[-1] - t[0]) / (t.size -1)  # in minutes

    sigt_mean       = np.mean(sigt)
    sigt_var        = np.var(sigt)
    sigt_std        = np.std(sigt)
    sigt_var        = np.var(sigt)
    sigt_err        = sigt_std / np.sqrt(sigt.size)

    print("t:    size:"       , t.size        , "\n", t)
    print("sigt: size:"       , sigt.size     , "\n", sigt)
    #print "sigt_win: size:"  , sigt_win.size , "\n", sigt_win


# figure and canvas ###################################################
    #~figEvalFFT = plt.figure(3, facecolor = "#C9F9F0") # blueish tint
    #~plt.clf()
    figEvalFFT = plt.figure(facecolor = "#C9F9F0") # blueish tint
    vprint("figEvalFFT: open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))
    #~try:
        #~plt.clf()
        #~vprint("Eval_plotFFT: Did plt.clf()")
    #~except Exception as e:
        #~srcinfo = "Eval_plotFFT: plt.clf() failed"
        #~exceptPrint(e, sys.exc_info(), srcinfo)


    # canvas - this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvas3 = FigureCanvas(figEvalFFT)
    canvas3.setFixedSize(1800, 700)
    navtoolbar = NavigationToolbar(canvas3, self)

# Data vs Time ################################################################
    plt.subplot (2,4,2)
    plt.title   ("Time Counts", fontsize=12, loc = 'left')
    subTitle = "Recs:" + str(sigt.size)
    plt.title   (subTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel  ("Time ({})".format(timeunit), fontsize=12)
    plt.ylabel  ("Count Rate  " + yunit, fontsize=12)
    plt.grid    (True)
    plt.ticklabel_format(useOffset=False)

    plt.plot    (t, sigt        ,  linewidth=0.4, color='red'   , label ="Time Domain" , marker="o", markeredgecolor='red'   , markersize=markersize)

# Autocorrelation vs Lag #########################################################
# calculations
    asigt = sigt - sigt_mean
    #print "np.mean(sigt) , np.var(sigt) :", np.mean(sigt),  np.var(sigt)
    #print "np.mean(asigt), np.var(asigt):", np.mean(asigt), np.var(asigt)

    asigtnorm = np.var(asigt) * asigt.size  # to normalize autocorrelation
    ac = np.correlate(asigt, asigt, mode='full') / asigtnorm
    #ac = ac[ac.size/2:]
    ac = ac[int(ac.size/2):]
    #print "ac: len:", ac.size
    #print "ac:", "\n", ac

# autocorrelation plot
    aax1 =  plt.subplot(2,4, 5)

    plt.title   ("Autocorrelation (normalized) vs. Lag Period", fontsize=11, loc = 'left', y = 1.08)
    plt.xlabel  ("Lag Period ({})".format(timeunit), fontsize=12)
    plt.ylabel  ("Autocorrelation", fontsize=12)
    plt.grid    (True)
    #plt.ticklabel_format(useOffset=False)

    aax2 = aax1.twiny()

    # how many points to show enlarged?
    for i in range(t.size):
        if ac[i] < 0: break

    tindex = min(i, t.size * 0.01)
    tindex = max(25, tindex, 60./(cycletime * 60.))
    tindex = int(tindex)  # Warning: ./geigerlog:3483: VisibleDeprecationWarning: using a non-integer number instead of an integer will result in an error in the future
                          # aax2.plot(tnew[:tindex], ac[:tindex], linewidth= 2.0, color='blue' , label ="Expanded Lag Period - Top Scale" , marker="o", markeredgecolor='blue'  , markersize=markersize*2)
                          # What is the reason ?????
    #print "tindex:", tindex

    tnew = t - t[0]
    aax1.plot(tnew,          ac         , linewidth= 1.0, color='red'  , label ="Full Lag Period - Bottom Scale" , marker="o", markeredgecolor='red'   , markersize=markersize * 2)
    #aax1.legend(loc='upper right', fontsize=12)

    aax2.plot(tnew[:tindex], ac[:tindex], linewidth= 2.0, color='blue' , label ="Expanded Lag Period - Top Scale" , marker="D", markeredgecolor='blue'  , markersize=markersize * 6)
    #print "ac:", ac[:10]

    #plt.legend(loc='upper right', fontsize=12)
    plt.legend(loc='upper right', fontsize=8)

    for a in aax1.get_xticklabels():
        #a.set_color("red")
        #a.set_weight("bold")
        pass

    for a in aax2.get_xticklabels():
        a.set_color("blue")
        a.set_weight("bold")

# FFT plots
# calculations
    # using amplitude spectrum, not power spectrum; power would be freq^2
    freq                = np.abs(np.fft.rfft(sigt     ))
    #freq2              = np.abs(np.fft.rfft(sigt2    ))
    print("freq:"       , len(freq)     , "\n", freq)
    #for i in range(0,100):  print freq[i]

    if use_window_functions:
        freq_win        = np.abs(np.fft.rfft(sigt_win ))
        #print "freq_win:"   , len(freq_win) , "\n", freq_win
        #for i in range(0,100):  print freq_win[i]

    f = np.fft.rfftfreq(t.size, d = cycletime)
    #print "f:   len:", f.size, "\n", f

    p  = np.reciprocal(f[1:])  # skipping 1st value frequency = 0
    #print "Period: len:", p.size, "\n", p


# Plot FFT vs Time #########################################################
    plt.subplot(2, 4, 1)
    plt.title("FFT Spectrum vs. Time Period", fontsize=12, loc = 'left')
    subTitle = "Recs:" + str(freq.size)
    plt.title   (subTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel("Time Period ({})".format(timeunit), fontsize=12)
    plt.ylabel("FFT Amplitude", fontsize=12)
    plt.grid(True)
    plt.ticklabel_format(useOffset=False)

    plt.loglog(p, freq[1:]        , linewidth= 0.4, color='red'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)

# Plot FFT vs Frequency ####################################################
    plt.subplot(2, 4, 6)
    #plt.title("FFT Spectrum vs. Frequency", fontsize=12, loc = 'left')
    plt.title("FFT Counts", fontsize=12, loc = 'left')
    subTitle = "Recs:" + str(freq.size)
    plt.title   (subTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel("Frequency ({})".format(frequencyunit), fontsize=12)
    plt.ylabel("FFT Amplitude", fontsize=12)
    plt.grid(True)
    plt.ticklabel_format(useOffset=False)

    plt.semilogy (f[1:], freq[1:]     , linewidth= 0.4, color='red'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)


# convolution plots ####################################################

    # rect for convolution - nr values of 1, followed by zeros
    nr = int(60 * 0.2)  # nr = 12
    nr = 60

    rect = np.zeros(sigt.size)
    for i in range(nr):
        rect[i] = 1
    print("rect:", len(rect), rect)

    # time axis
    bf = t[:rect.size]

# Plot Rectangle Signal vs time

    plt.subplot (2, 4, 3)
    plt.title   ("Time Rectangle", fontsize=12, loc = 'left')
    subTitle = "Recs:" + str(rect.size)
    plt.title   (subTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel  ("Time ({})".format(timeunit), fontsize=12)
    plt.ylabel  ("Signal Value", fontsize=12)
    plt.grid    (True)
    plt.ticklabel_format(useOffset=False)
    plt.plot (bf, rect     , linewidth= 1.0, color='red'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize*4)


# FFT of Signal vs Frequency ####################################################

    cfreq = np.abs(np.fft.rfft(rect     ))
    print("cfreq:   len:", cfreq.size, "\n", cfreq)

    f = np.fft.rfftfreq(t.size, d = cycletime)
    print("f:   len:", f.size, "\n", f)

    p  = np.reciprocal(f[1:])  # skipping 1st value frequency = 0
    print("Period: len:", p.size, "\n", p)

    plt.subplot (2, 4, 7)
    plt.title   ("FFT Rectangle", fontsize=12, loc = 'left')
    subTitle = "Recs:" + str(cfreq.size)
    plt.title   (subTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel  ("Frequency ({})".format(frequencyunit), fontsize=12)
    plt.ylabel  ("FFT Amplitude", fontsize=12)
    plt.grid    (True)
    plt.ticklabel_format(useOffset=False)

    plt.semilogy (f[1:], cfreq[1:]     , linewidth= 0.4, color='red'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)


# last columns
# upper

    csigt = scipy.signal.convolve(rect, sigt ) * (60 / nr)
    csigt = csigt[nr:len(sigt) + nr]
    print("csigt:", len(csigt), csigt)

    plt.subplot (2, 4, 4)
    plt.title   ("Time (Counts CNV Rectangle)", fontsize=12, loc = 'left')
    subTitle = "Recs:" + str(csigt.size)
    plt.title   (subTitle, fontsize=10, fontweight='normal', loc = 'right')

    plt.xlabel  ("Time ({})".format(timeunit), fontsize=12)
    plt.ylabel  ("Count Rate CPM", fontsize=12)
    plt.grid    (True)
    plt.ticklabel_format(useOffset=False)

    plt.plot (t[:-nr], csigt[:-nr]     , linewidth= 0.4, color='red'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)

# lower
    ccfreq = cfreq * freq

    plt.subplot (2, 4, 8)
    plt.title   ("FFT (Counts CNV Rectangle)", fontsize=12, loc = 'left')
    subTitle = "Recs:" + str(cfreq.size)
    plt.title   (subTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel  ("Frequency ({})".format(frequencyunit), fontsize=12)
    plt.ylabel  ("FFT Amplitude", fontsize=12)
    plt.grid    (True)
    plt.ticklabel_format(useOffset=False)

    plt.semilogy (f[1:], ccfreq[1:]     , linewidth= 0.4, color='red'   , label ="FFT" , marker="o", markeredgecolor='red'   , markersize=markersize)



# arrange sub plots
    plt.subplots_adjust(hspace=0.4, wspace=0.3, left=.05, top=0.95, bottom=0.09, right=.97)

# textboxes ################################################################
    labout_left  = QTextBrowser() # label to hold some data on left side
    labout_left.setLineWrapMode(QTextEdit.NoWrap)
    labout_left.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
    labout_left.setMinimumHeight(150)

    #labout_left.append("{:22s}= {}"                             .format('File'               , os.path.basename(gglobs.currentDBPath)))
    labout_left.append("{:22s}= {}"                             .format('File'               , DataSrc))
    labout_left.append("{:22s}= {}"                             .format("No of Records"      , t.size))
    labout_left.append("{:22s}= {:4.2f}"                        .format("Count Rate Average" , sigt_mean))
    labout_left.append("{:22s}= {:4.2f} (Std.Dev:{:5.2f}, Std.Err:{:5.2f})"    .format("Count Rate Variance" , sigt_var, sigt_std, sigt_err))
    labout_left.append("{:22s}= {:4.2f} sec (overall average)"  .format("Cycle Time"         , cycletime * 60.)) # t is in minutes
    labout_left.append("{:22s}= {:4.2f} "                       .format("A.corr(lag=  0   sec)", ac[0]))
    labout_left.append("{:22s}= {:4.2f} "                       .format("A.corr(lag={:5.1f} sec)".format(tnew[1] *60.), ac[1]))
    labout_left.append("{:22s}= {:4.2f} "                       .format("A.corr(lag={:5.1f} sec)".format(tnew[2] *60.), ac[2]))
    #labout_left.append("{:22s}= {:4.2f} "                       .format("Autoc(lag={:5.1f} sec)".format(tnew[3] *60.), ac[3]))

    labout_right  = QTextBrowser() # label to hold some data on right side
    labout_right.setLineWrapMode(QTextEdit.NoWrap)
    labout_right.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
    labout_right.setMinimumHeight(120)

    fftmax      = np.max    (freq[1:])
    fftmaxindex = np.argmax (freq[1:]) + 1
    f_max       = f         [fftmaxindex ]

    labout_right.append("{:22s}= {:4.0f}"              .format("FFT(f=0)"         , freq[0]) )
    #labout_right.append("{:22s}= {:4.0f}"              .format("len(t)"         , len(t)) )
    labout_right.append("{:22s}= {:4.2f} (= FFT(f=0)/No of Records)".format("Count Rate Average", freq[0] / len(t)) )
    labout_right.append("{:22s}= {:4.2f}"              .format("Max FFT(f>0)"     , fftmax))
    labout_right.append("{:22s}= {}"                   .format("  @ Index"        , fftmaxindex))
    labout_right.append("{:22s}= {:4.4f}"              .format("  @ Frequency"    , f_max ))
    try:
        labout_right.append("{:22s}= {:4.4f}"              .format("  @ Period"       , p[fftmaxindex] ))
    except:
        labout_right.append("{:22s}= {:s}"              .format("  @ Period"       , "undefined" ))


# Pop Up  #################################################################
    d       = QDialog()
    d.setWindowIcon(self.iconGeigerLog)
    d.setFont(self.fontstd)
    d.setWindowTitle("FFT & Autocorrelation" + winTitleLabel)
    #d.setMinimumHeight(gglobs.window_height)
    #d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    d.setWindowModality(Qt.WindowModal)

    bbox    = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: d.done(0))

    layoutH   = QHBoxLayout()
    layoutH.addWidget(labout_left)
    layoutH.addWidget(labout_right)


    layoutV   = QVBoxLayout(d)
    layoutV.addWidget(navtoolbar)
    layoutV.addWidget(canvas3)
    layoutV.addLayout(layoutH)
    layoutV.addWidget(bbox)

    figEvalFFT.canvas.draw_idle()
    d.exec_()
    plt.close(figEvalFFT)

#**End Eval_plotFFT ***********************************************************
