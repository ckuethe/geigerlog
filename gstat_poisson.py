#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gstat_poisson.py - GeigerLog commands for poisson statistics

include in programs with:
    import gstat_poisson
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"


from gsup_utils   import *


def plotPoisson():
    """Plotting a Poisson Fit to a histogram of the data"""


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
    # hist = np.empty(len(bins) - 1)
    # for i in range(0, len(bins) - 1):
    #     stepsum = 0
    #     ll0 = bins[i ]
    #     hl0 = bins[i + 1]
    #     dl0 = hl0 - ll0
    #     for j in range(0, step):
    #         ll = ll0 - (dl0 / 2 / step) + dl0 /step * j
    #         hl = ll + dl0 / step
    #         stepsum += len( x[((x>=ll) & (x<hl))] )
    #         #print("i, j, ll0, hl0,  ll, hl, stepsum: ", i, j, ll0, hl0, ll, hl, stepsum)
    #     hist[i] = stepsum
    # mdprint(defname, "manual histogram: len(hist):", len(hist), "  ", hist[0:3])

    # numpy.histogram(a, bins=10, range=None, density=None, weights=None)
    # hist2, bin_edges2 = np.histogram(x, bins=len(bins) - 1, range=(x.min(), x.max()))
    # hist2, bin_edges2 = np.histogram(x, bins=len(bins) - 1)




# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# chi squared stuff  ----------------------------------------------------------
# since 22.Juli 2021 I noticed this error coming up in all data files, even synthetic data:
# Chi-squared Test Poisson: Exception: For each axis slice, the sum of the observed frequencies
# must agree with the sum of the expected frequencies to a relative tolerance of 1e-08, but
# the percent differences are: 1.3829332101245581e-05
# conclusion: some change in the scipy lib!
#             --> remove the whole chi-square calculation
#                 remove also Kolmogorov-Smirnoff calculation

    #~obs     = hist
    #~exp     = pdfs
    #~mini    = 0
    #~maxi    = len(obs)

    #~# find where obs and exp are both > 5
    #~# first the left side
    #~for i in range(len(obs)):
        #~#print("Left:   i={}, obs={:9.0f}, exp={:9.2f}".format(i, obs[i], exp[i] ))
        #~if obs[i] >=5 and exp[i] >= 5:
            #~#print("mini--> i={}, obs= {}, exp={}".format(i, obs[i], exp[i]))
            #~mini = i
            #~break

    #~# now the right side
    #~for i in range(mini, len(obs) ):
        #~#print("Right: i={}, obs={:9.0f}, exp={:9.2f}".format(i, obs[i], exp[i] ))
        #~if obs[i] <= 5 or exp[i] <= 5:
            #~#print("maxi--> i={}, obs= {}, exp={}".format(i, obs[i], exp[i]))
            #~maxi = i
            #~break

    #~# the ignored values on the right side
    #~for i in range(maxi, len(obs) ):
        #~pass
        #~#print("Rest:  i={}, obs={:9.0f}, exp={:9.2f}".format(i, obs[i], exp[i] ))

    #~wprint(defname + "mini:{}, maxi:{}, diff:{}".format(mini, maxi, maxi - mini))



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
    #mdprint(defname + txtChi2Poiss)


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

    #~# calc chi2 for Poisson
    #~try:
        #~ddofPoiss               = 1
        #~dofPoiss                = len(hist[mini:maxi]) - ddofPoiss
        #~chi2Poiss, pchi2Poiss   = scipy.stats.chisquare(hist[mini:maxi], f_exp=pdfs[mini:maxi],    ddof=ddofPoiss, axis=None)
        #~# testing same fucntion gives p=100%
        #~#chi2Poiss, pchi2Poiss   = scipy.stats.chisquare(pdfs[mini:maxi], f_exp=pdfs[mini:maxi],    ddof=ddofPoiss, axis=None)
        #~txtChi2Poiss            = "Chi-squared Test Poisson:  DoF = {:1d}, chi² = {:5.1f}, p = {:2.1%}".format(dofPoiss, chi2Poiss, pchi2Poiss)
    #~except Exception as e:
        #~dprint("Chi-squared Test Poisson: Exception: ", e)
        #~txtChi2Poiss            = "Chi-squared Test Poisson:  cannot be calculated!"
    #~mdprint(defname + txtChi2Poiss)

    #~# calc chi2 for Normal
    #~try:
        #~ddofNorm                = 2
        #~dofNorm                 = len(hist[mini:maxi]) - ddofNorm
        #~chi2Norm, pchi2Norm     = scipy.stats.chisquare(hist[mini:maxi], f_exp=pdfnorm[mini:maxi], ddof=ddofNorm, axis=None)
        #~# testing same fucntion gives p=100%
        #~#chi2Norm, pchi2Norm     = scipy.stats.chisquare(pdfnorm[mini:maxi], f_exp=pdfnorm[mini:maxi], ddof=ddofNorm, axis=None)
        #~txtChi2Norm             = "Chi-squared Test Normal :  DoF = {:1d}, chi² = {:5.1f}, p = {:2.1%}".format(dofNorm, chi2Norm, pchi2Norm)
    #~except Exception as e:
        #~dprint("Chi-squared Test Normal: Exception: ", e)
        #~txtChi2Norm             = "Chi-squared Test Normal:  cannot be calculated!"
    #~mdprint(defname + txtChi2Norm)

# END chi squared stuff  ------------------------------------------------------
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# code inactivated for same reason as chi-squared stuff above
#~# Kolmogorov-Smirnoff stuff ---------------------------------------------------
    #~#print("avgx: ", avgx)
    #~obs     = hist
    #~exp     = pdfs
    #~#print("blue values:\n", obs)
    #~#print("red  values:\n", exp)

    #~#print(scipy.stats.kstest(exp,'poisson', args=(20,), alternative='less'))

    #~ks_stats_p, ks_pval_p = scipy.stats.kstest(x, 'poisson', args=(avgx,))
    #~ks_stats_n, ks_pval_n = scipy.stats.kstest(x, 'norm'   , args=(avgx,))
    #~#print("========================= x_norm    : avg:", avgx, ks_stats_n, ks_pval_n)
    #~#print("========================= x_pois    : avg:", avgx, ks_stats_p, ks_pval_p)

    #~obs_cum  = np.empty_like(obs)
    #~exp_cum  = np.empty_like(exp)

    #~for i in range(0, len(obs) +1):
        #~obs_cum = np.cumsum(obs[0:i])
        #~exp_cum = np.cumsum(exp[0:i])

    #~#print("obs_cum: \n", obs_cum)
    #~#print("exp_cum: \n", exp_cum)

    #~#diff  = np.empty_like(obs)
    #~#for i in range(0, len(obs)):
    #~#    diff[i] = obs_cum[i] - exp_cum[i]
    #~#print("diff: \n", diff)
    #~#print("diff: \n", np.absolute(diff))

    #~#diffmax = np.max(np.absolute(diff))
    #~#print("diffmax: ", diffmax)

#~# END   Kolmogorov-Smirnoff stuff ---------------------------------------------
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


#    # chi stuff all removed, see above
#    labout.append(txtChi2Norm)

#    labout.append("Kolmogorov-Smirnow Poisson Test: ")
#    labout.append("Poisson :  statistic = {:5.3f}, pvalue= {:2.3%}".format(ks_stats_p, ks_pval_p))
#    labout.append("Normal  :  statistic = {:5.3f}, pvalue= {:2.3%}".format(ks_stats_n, ks_pval_n))


    defname = "plotPoisson: "
    mdprint(defname)
    setIndent(1)

    data0       = g.logSliceMod

    # if data0 is None or len(data0) == 0:
    #     msg = defname + "No data available"
    #     g.exgg.showStatusMessage(msg)
    #     mdprint(defname, msg)
    #     setIndent(0)
    #     return


    vindex      = g.exgg.select.currentIndex()
    vname       = list(g.VarsCopy)[vindex]
    vnameFull   = g.VarsCopy[vname][0]
    yunit       = vnameFull
    DataSrc     = os.path.basename(g.currentDBPath)
    # cycletime   = (t[-1] - t[0]) / (t.size - 1)  # in minutes     # needs time, which is not read


    # continue only when variable is checked for display
    if not g.exgg.varDisplayCheckbox[vname].isChecked():
        msg = "Variable {} is not checked for display".format(vname)
        g.exgg.showStatusMessage(msg)
        vprint(defname, msg)
        setIndent(0)
        return


    if data0 is None or len(data0) == 0:
        msg = "No data available"
        g.exgg.showStatusMessage(msg)
        mdprint(defname, msg)
        setIndent(0)
        return

    data0 = data0[vname]

    # Fehler sollten doch abgefangen werden in applyValueFormula?
    # müßte das nicht applyGraphFormula sein???
    # if   g.useGraphScaledData:  x0 = applyValueFormula(vname, data0, g.GraphScale[vname], info=defname)
    if   g.useGraphScaledData:  x0 = applyGraphFormula(vname, data0, g.GraphScale[vname], info=defname)
    else:                       x0 = data0


    # clean the data from nan:
    xmask = np.isfinite(x0)      # mask for nan values in x0
    x     = x0[xmask]
    if len(x) == 0:
        msg = defname + "No data available"
        g.exgg.showStatusMessage(msg)
        mdprint(defname, msg)
        setIndent(0)
        return


    setBusyCursor()

    ######################################
    # to show histogram of delta between 2 consecutive counts
    # zeigt KEINE exp function! Deadtime effekt?
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


    # np.nanXYZ: all values excluding NANs! though there shouldn't be any,
    # as they were eliminated above by the masking. But it does not hurt
    lenx  = len(x)
    sumx  = np.nansum (x)
    avgx  = np.nanmean(x)
    varx  = np.nanvar (x)
    stdx  = np.nanstd (x)
    minx  = np.nanmin (x)
    maxx  = np.nanmax (x)
    std95 = stdx * 1.96           # +/- std95 is range for 95% of all values

    mdprint(defname, "count data: lenx:{:0,.0f}  sumx:{:0,.0f}  avgx:{:0,.3f}  varx:{:0,.3f}  stdx:{:0,.3f}  minx:{:0,.0f}, maxx:{:0,.0f}, std95%:{:0,.3f}".\
                format(lenx,   sumx,         avgx,          varx,         stdx,         minx,         maxx,         std95))

    ###########################################################################################
    # get R-squared
    def getRsquared(ydata, ymodel):
        """
        Calculate r-squared based on ydata and ymodel
        input:  ydata, ymodel
        return: r2, dB (=decibels)
        """

        defname = "getRsquared: "

        try:
            ss_res = np.sum((ydata - ymodel)         ** 2)      # residual sum of squares to mmodel
            ss_tot = np.sum((ydata - np.mean(ydata)) ** 2)      # total sum of squares to average
            r2     = float(1 - (ss_res / ss_tot))               # r-squared
            dB     = float(10 * np.log10(ss_tot / ss_res))      # dezibel (??) printed as SNR (Signal To Noise Ratio)
        except Exception as e:
            exceptPrint(e, defname)
            ss_res = ss_tot = r2 = dB = g.NAN

        # mdprint(defname, "getRsquared: ", "ss_res: ", ss_res, "  ss_tot: ", ss_tot, "  R2: ", r2, "  dB: ", dB)

        return (r2, dB)
    ###########################################################################################

# make the bin limits and bin width
    colmin = 0
    # colmax = 30
    colmax = 40    # does it make it look nicer???? YES!!!

    # left:  take the lower of (the lowest count rate) and (the average minus 2 StdDev), but must be at least zero
    bin_min    = int(max(colmin,  min(minx , avgx - (std95 * 2))))

    # right:  take the higher of (the highest count rate) and (the average plus 2 StdDev) and (number of at least 30 columns)
    bin_max    = int(max(colmax,            avgx + (std95 * 2)))

    # limit the total no of bins to 30 by making the bins wider, but keep width at least at 1
    bin_width  = int(max(1, int((bin_max - bin_min) / colmax)))
    bin_total  = int((bin_max - bin_min) / bin_width) + 1
    mdprint(defname, "Poisson fits: bin_width: {}, bin_min: {}, bin_max: {}, bin_total: {}".format(bin_width, bin_min, bin_max, bin_total))

# create all the bin left edges
    bins    = np.empty(bin_total + 1)
    bins[0] = int(bin_min)
    for i in range(1, bin_total + 1):
        bins[i] = int(bins[i - 1] + bin_width)  # make the left edges
    # rdprint(defname, "bins: len(): ", len(bins), "  ", bins)


# get the histogram for those bins
    hist, bin_edges2 = np.histogram(x, bins=bins )
    # rdprint(defname, "bins == bin_edges2: ", bins == bin_edges2)

    # print each bin and totals
    # if g.devel:
    #     print("DVL No. of bins: {:<2n}  Sum all bins: {:<10.3f}  Total recs: {:<10.3f}".format(len(bins) - 1, sum(hist), len(x)))
    #     for i in range(0, len(bin_edges2) - 1):
    #         print("DVL Bin #{:<2d}  hist: {:<10.3f}    bins-leftEdge: {:<10.3f}".format(i + 1, hist[i], bin_edges2[i]))
    #     print()


# create Default Poisson dist
    # create the Poisson dist for the bins from above histogram
    pdfs = []
    for i in range(int(bins[0]), int(bins[-1]), int(bin_width)):
        bin_widthsum = 0
        for j in range(0, bin_width):
            bin_widthsum += scipy.stats.poisson.pmf(i + j, avgx)
        pdfs.append(bin_widthsum * lenx)
    mdprint(defname, "Default Poisson - len(pdfs):", len(pdfs), "  ", pdfs[0:6], " ...")

    # get r2
    r2, PoissdB = getRsquared(hist, pdfs)
    mdprint(defname, "R2 Poisson: {:+0.3f}  SNR: {:+0.1f}".format(r2, PoissdB))

    # needed when no fit is requested
    last_pdfs = pdfs
    last_hist = hist


# create Default Poiss-like Normal with StdDev = SQRT(Average)
    if g.NormalPoissCurveFit:
        pdfnorm = []
        if avgx >= 0:
            pdfnorm = []
            for i in range(int(bins[0]), int(bins[-1]), int(bin_width)):
                bin_widthsum = 0
                for j in range(0, bin_width):
                    bin_widthsum += scipy.stats.norm.pdf(i + j , avgx, scale=np.sqrt(avgx))
                pdfnorm.append(bin_widthsum * lenx)
            mdprint(defname, "Default Normal len(pdfnorm):", len(pdfnorm), "  ", pdfnorm[0:3], " ...")

            # get r2
            r2NP, NormdBP = getRsquared(hist, pdfnorm)
            mdprint(defname, "R2 Normal (NP): {} SNR: {:0.0f}".format(r2NP, NormdBP))
        else:
            pdfnorm = [g.NAN] * (len(bins) - 1)
            r2NP, NormdBP = g.NAN, g.NAN


# create the cumulative Poisson hist and dist
    if g.CumProbDist:
        # make histogram
        cumhist = np.empty(len(bin_edges2) - 1)
        cumhist[0] = 0 + hist[0]
        for i in range(1, len(bin_edges2) - 1):
            cumhist[i] = cumhist[i - 1] + hist[i]
            # print("i: {:2n}  cumhist: {}".format(i, cumhist[i]))

        # sum up the Poisson dist for the bins from above histogram
        if g.CumPoissCurveFit:
            cpdfs = []
            for i in range(int(bins[0]), int(bins[-1]), int(bin_width)):
                bin_widthsum = scipy.stats.poisson.cdf(i + (bin_width - 1), avgx)   # take only the rightmost bin when more than 1
                cpdfs.append(bin_widthsum * lenx)
            mdprint(defname, "Cumulative Poisson len(cpdfs):", len(cpdfs), "  ", cpdfs[0:3], " ...")

            # get r2
            r2CP, CPoissdB = getRsquared(cumhist, cpdfs)
            mdprint(defname, "CP Poisson: R2: {}  SNR: {:0.0f}".format(r2CP, CPoissdB))


### inactive
# # ----- BEGIN if g.NormalCurveFit:-------------------------------------------------------------------------------------------------------------
#     if g.NormalCurveFit:
#         # Normal with StdDev as calculated from data
#         if minx == maxx:
#             # if equal add some difference
#             # take the lowest count rate - 10
#             bin_min    = minx - 10

#             # take the highest count rate + 10
#             bin_max    = maxx + 10
#         else:
#             # take the lowest count rate
#             bin_min    = minx

#             # take the highest count rate
#             bin_max    = maxx


#         # limit the total no of bins to 30 by making the bins wider, but keep width at least at 1
#         bin_width        = (bin_max - bin_min) / 30
#         mdprint(defname, "g.NormalCurveFit: bin_width: ", bin_width, "  bin_min: ", bin_min, "bin_max: ", bin_max)
#         bin_total        = int((bin_max - bin_min) / bin_width) + 1
#         #print("  bin_width: {}, bin_min: {}, bin_max: {}, bin_total: {}".format(bin_width, bin_min, bin_max, bin_total))

#         bins    = np.empty(bin_total + 1)
#         bins[0] = bin_min
#         for i in range(1, bin_total + 1):
#             bins[i] = bins[i - 1] + bin_width

#         hist, bin_edges2 = np.histogram(x, bins=bins )

#         if g.devel:
#             # print each bin and totals
#             print("DVL No. of bins: {:<2n}  Sum all bins: {:<10.3f}  Total recs: {:<10.3f}  bins-width: {:8.3f}".format(len(bins) - 1, sum(hist), len(x), bins[1] - bins[0]))
#             for i in range(0, len(bin_edges2) - 1):
#                 print("DVL Bin #{:<2d}  hist: {:<10.3f}    bins-leftEdge: {:<10.3f}".format(i + 1, hist[i], bin_edges2[i]))
#             print()


#         pdfnormStd = []
#         for i in range(0, len(bins) - 1):
#             bin_mid = (bins[i] + bins[i + 1]) / 2
#             bin_widthsum = scipy.stats.norm.pdf(bin_mid , avgx, scale=stdx)
#             bin_widthsum = bin_widthsum * bin_width
#             pdfnormStd.append(bin_widthsum * lenx)
#         mdprint(defname, "Default Normal StdDev len(pdfnormStd):", len(pdfnormStd), "  ", pdfnormStd[0:3], " ...")

#         # get r2
#         r2NS, NormdBS = getRsquared(hist, pdfnormStd)
#         mdprint(defname, "R2Normal (NS): {}  SNR: {:0.0f}".format(r2NS, NormdBS))

#         pdfs    = pdfnormStd    # pdfs will be used to print the curve data in labout

# # ----- END if g.NormalCurveFit:-------------------------------------------------------------------------------------------------------------


    fig2 = plt.figure(facecolor = "#E7F9C9", dpi=g.hidpiScaleMPL)
    g.plotPoissonFigNo = plt.gcf().number
    # mdprint("plotPoisson: open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))



    plt.suptitle("Histogram", fontsize=12 )
    RsubTitle = DataSrc + "  Recs:" + str(x.size)
    plt.title(RsubTitle, fontsize=10, fontweight='normal', loc = 'right')
    plt.xlabel("Variable {}".format(yunit), fontsize=12)
    plt.ylabel("Frequency of Occurence", fontsize=12)
    plt.grid(True)
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.14, top=0.89, bottom=0.11, right=.97)
    plt.ticklabel_format(useOffset=False)

    # canvas - this is the Canvas Widget that displays the `figure`; it takes the `figure` instance as a parameter to __init__
    canvas2 = FigureCanvas(fig2)
    # canvas2.setFixedSize(650, 500)
    canvas2.setMinimumHeight(500)

    #
    # plot histogram and statistics curves #########################################
    #

    if g.ProbDist:
        # plot Prob histogram
        # plt.bar(bins[:-1],  hist, color="cornflowerblue", align='center', width=bin_width * 0.85, label ="avg = {:0.2f}\nvar = {:0.2f}".format(avgx, varx))
        plt.bar(bins[:-1],  hist, color="cornflowerblue", align='center', width=bin_width * 0.75, label ="avg = {:0.2f}\nvar = {:0.2f}".format(avgx, varx))

        if g.PoissCurveFit:
            # Poisson curve
            plt.plot(bins[:-1], pdfs,           color='red',       linewidth=3,                           label = "P r2={:0.3f}".format(r2))

            # Poisson curve residuals
            plt.plot(bins[:-1], hist - pdfs,    color='orangered', linewidth=1, marker='o', markersize=3, label = "P Residuals")

            last_pdfs = pdfs
            last_hist = hist

        # Normal curve based on StdDev=sqrt(mean)
        if g.NormalPoissCurveFit:
            # Normal curve
            plt.plot(bins[:-1], pdfnorm,        color='black',     linewidth=3,                           label ="NP r2={:0.3f}".format(r2NP))

            # Normal curve residuals
            plt.plot(bins[:-1], hist - pdfnorm, color='black',     linewidth=1, marker='s', markersize=3, label="NP Residuals")

            last_pdfs = pdfnorm
            last_hist = hist

    else:
        # plot CumProb histogram
        plt.bar(bins[:-1],  cumhist, color="turquoise", align='center', width=bin_width * 0.85, label ="avg = {:0.2f}\nvar = {:0.2f}".format(avgx, varx))

        # Poisson cumulative
        if g.CumPoissCurveFit:

            # Cumulative Poisson curve
            plt.plot(bins[:-1], cpdfs,              color='blue', linewidth=3,                           label = "CP r2={:0.3f}".format(r2CP))

            # Cum Poiss Residuals
            plt.plot(bins[:-1], cumhist - cpdfs,    color='blue', linewidth=1, marker='o', markersize=3, label = "CP Residuals")

            last_pdfs = cpdfs
            last_hist = cumhist



# ##################
#     # currently not in use !!!
#     # Normal curve based on StdDev calculated from data
#     if g.NormalCurveFit:
#         # Normal curve
#         plt.plot(bins[:-1], pdfnormStd,        color='green',  linewidth=2,                           label ="NS r2={:0.3f}".format(r2NS))
#
#         # Normal curve residuals
#         plt.plot(bins[:-1], hist - pdfnormStd, color='green',  linewidth=1, marker='s', markersize=3, label="NS Residuals")
# ##################

    # best place for Legend found with "best" (is default anyway)   -  gives "Warning": using "best" could take long with many data
    # plt.legend(loc="best", fontsize=10, prop={"family":"monospace"})
    if avgx > (bins[0] + bins[-1]) / 2: location = "upper left"
    else:                               location = "upper right"
    plt.legend(loc=location, fontsize=10, prop={"family":"monospace"})


    #
    # make text field with info on histogram, data, and statistics
    #
    labout = QTextBrowser()
    labout.setFont(g.fontstd)
    labout.setLineWrapMode(QTextEdit.NoWrap)
    labout.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
    labout.setMinimumHeight(250)

    # Histogram and Fit Properties
    labout.append("<b>Histogram Properties</b>:")
    labout.append("Bin  Bin Values   Frequency    % of    Curve-Fit     Residuals")
    labout.append("No. Width:{:<6.3f} (blue col)   Total   thick line     thin line".format(bin_width))

    for i in range(0, len(hist)):
        if (g.ProbDist and (g.PoissCurveFit or g.NormalPoissCurveFit) or (g.CumProbDist and g.CumPoissCurveFit)):
            Fiti = customformat(last_pdfs[i],           11, 4, thousand=True)
            Resi = customformat(last_hist[i] - last_pdfs[i], 11, 4, thousand=True)
        else:
            Fiti = Resi = "-"
        labout.append("{:3d}  {:10,.3f}  {:10,.4g} {:6.2f}%  {:>11s}   {:>11s}".format(i + 1, bins[i], last_hist[i], last_hist[i]*100 / lenx, Fiti, Resi))

    if (g.ProbDist and (g.PoissCurveFit or g.NormalPoissCurveFit)):
        sumF = customformat(sum(last_pdfs),             11, 4, thousand=True)
        sumR = customformat(sum(last_hist - last_pdfs), 11, 4, thousand=True)
    elif (g.CumProbDist and g.CumPoissCurveFit):
        sumF = customformat(last_pdfs[-1],              11, 4, thousand=True)
        sumR = customformat(sum(last_hist - last_pdfs), 11, 4, thousand=True)
    else:
        sumF = sumR = "-"

    labout.append("Totals =         {:10,.0f} 100.00%  {:>11s}   {:>11s}\n".format(sum(last_hist), sumF, sumR))


    # Data Properties
    labout.append("\n<b>Data Properties:</b>")
    labout.append("File      = {}"                                                              .format(g.currentDBPath))
    labout.append("Records   = {:8.0f}"                                                         .format(x.size))
    labout.append("Average   = {:8.2f}"                                                         .format(avgx))
    labout.append("Variance  = {:8.2f} (Note: same as Average if true Poisson Distribution)"    .format(varx))


    labout.append("Std.Dev.  = {:8.2f}"                                                         .format(stdx))
    labout.append("Sqrt(Avg) = {:8.2f} (Note: same as Std.Dev. if true Poisson Distribution)"   .format(np.sqrt(avgx) if avgx >= 0 else g.NAN))
    labout.append("Std.Err.  = {:8.2f}"                                                         .format(stdx / np.sqrt(x.size)))
    labout.append("Min : Max = {:8.2f} : {:<8.2f}"                                              .format(minx, maxx))
    labout.append("Skewness  = {:8.2f} (Note: 0:Norm.Dist.; skewed to: +:right   -:left)"       .format(scipy.stats.skew    (x) ))
    labout.append("Kurtosis  = {:8.2f} (Note: 0:Norm.Dist.; shape is:  +:pointy: -:flat)"       .format(scipy.stats.kurtosis(x) ))
    labout.append("")

    # Goodness of Fit
    labout.append("<b>Fit Properties:</b>")
    sP   = "Poisson"
    sCP  = "Cumulative Poisson"
    sNP  = "Normal (Poisson like)"
    sNS  = "Normal (Standard)"
    sPX  = sP  + "&nbsp;" * (21 - len(sP))
    sCPX = sCP + "&nbsp;" * (21 - len(sCP))
    sNPX = sNP + "&nbsp;" * (21 - len(sNP))
    sNSX = sNS + "&nbsp;" * (21 - len(sNS))

    if   (g.ProbDist and (g.PoissCurveFit or g.NormalPoissCurveFit)):
        if g.PoissCurveFit:       labout.append("Goodness of Fit <b>{:20s}</b> : r² = {:5.3f} SNR = {:0.0f} dB".format(sPX,  r2,   PoissdB))
        if g.NormalPoissCurveFit: labout.append("Goodness of Fit <b>{:20s}</b> : r² = {:5.3f} SNR = {:0.0f} dB".format(sNPX, r2NP, NormdBP))
    elif (g.CumProbDist and g.CumPoissCurveFit):
        labout.append("Goodness of Fit <b>{:20s}</b> : r² = {:5.3f} SNR = {:0.0f} dB".format(sCPX, r2CP, CPoissdB))
    else:
        labout.append("No Fit selected")

    labout.append("")

    ###########################################################################

    #
    # make checkboxes with layout
    #

    # Label Probability Distribution
    PDLabel = QRadioButton("Probability Distribution")
    PDLabel.setStyleSheet("QRadioButton {font:bold;}")
    PDLabel.setChecked(g.ProbDist)

    # Label Cumulative Probability Distribution
    CPDLabel = QRadioButton("Cumulative Probability Distribution")
    CPDLabel.setStyleSheet("QRadioButton {font:bold;}")
    CPDLabel.setChecked(g.CumProbDist)

    # Check Plot Poisson Fit
    checkbPPF = QCheckBox("Poisson Fit (P)")      # default is yes
    checkbPPF.setChecked(g.PoissCurveFit)

    # Check Plot Cumulative Poisson Fit
    checkbCPPF = QCheckBox("Cumulative \nPoisson Fit (CP)")
    checkbCPPF.setChecked(g.CumPoissCurveFit)

    # Check Plot Normal Fit
    checkbNORMAL = QCheckBox("Normal Fit (NP)\n(Poisson-like)")
    checkbNORMAL.setChecked(g.NormalPoissCurveFit)

    # Check Plot Normal Fit StdDev
    checkbNORMALS = QCheckBox("Normal Fit (NS)\n(Standard)")
    checkbNORMALS.setChecked(g.NormalCurveFit)

    layoutLabels = QHBoxLayout()
    layoutLabels.addWidget(PDLabel)
    layoutLabels.addWidget(CPDLabel)

    layoutSelects = QHBoxLayout()
    layoutSelects.addWidget(checkbPPF)
    layoutSelects.addWidget(checkbNORMAL)
    layoutSelects.addWidget(checkbCPPF)
    layoutSelects.addWidget(QLabel("   "))
    # layoutSelects.addWidget(checkbNORMALS)

    ###############################

    # setup dialog
    d = QDialog()
    g.plotPoissonPointer = d
    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("Poisson Test")
    d.setWindowModality(Qt.WindowModal)
    d.setMaximumWidth(1200)

    navtoolbar = NavigationToolbar(canvas2, d) # choice of parent does not matter?

    # show the cursor x, y position in the Nav toolbar
    ax1 = plt.gca()
    ax1.format_coord = lambda x,y: "x={:.1f}, y={:.1f}".format(x, y)

    okButton = QPushButton("OK")
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.done(0))

    selectButton = QPushButton("Plot")
    selectButton.setStyleSheet("QPushButton {font:bold;}")
    selectButton.setAutoDefault(False)
    selectButton.clicked.connect(lambda:  d.done(100))

    bbox = QDialogButtonBox()
    bbox.addButton(selectButton,  QDialogButtonBox.ActionRole)
    bbox.addButton(okButton,      QDialogButtonBox.ActionRole)

    layoutV = QVBoxLayout(d)
    layoutV.addWidget(navtoolbar)
    layoutV.addWidget(canvas2)
    layoutV.addLayout(layoutLabels)
    layoutV.addLayout(layoutSelects)
    layoutV.addWidget(bbox)
    layoutV.addWidget(labout)

    setNormalCursor()

# show window
    fig2.canvas.draw_idle()
    retval = d.exec()

    if retval == 100:
        g.ProbDist              = PDLabel.isChecked()
        g.CumProbDist           = CPDLabel.isChecked()

        g.PoissCurveFit         = checkbPPF.isChecked()
        g.CumPoissCurveFit      = checkbCPPF.isChecked()
        g.NormalPoissCurveFit   = checkbNORMAL.isChecked()
        # g.NormalCurveFit      = checkbNORMALS.isChecked()

        setIndent(0)
        g.plotPoissonPointer.close()                            # closes the dialog
        plt.close(g.plotPoissonFigNo)                           # closes the figure
        plotPoisson()                                           # re-plots

    plt.close(fig2)
    setIndent(0)

