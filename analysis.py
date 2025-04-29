# importing libraries
import numpy as np
from scipy.stats import chi2, ttest_1samp
from scipy.special import erf

# declaring the Analysis class
# this class is used to perform the analysis on the data
class Analysis:
    # this function is used to calculate the Chauvenet's criterion
    # it takes the data as input and returns the Chauvenet's criterion
    def chauvenet(self, data: np.ndarray):
        d = np.sort(data)
        μ = d.mean()
        σ = d.std(ddof=1)
        t = np.abs(d - μ) / σ
        p = 1 - erf(t/np.sqrt(2))
        P = p * len(d)
        return list(zip(d, P))

    # this function is used to calculate the chi-square analysis
    # it takes two dataframes as input and returns the chi-square analysis
    def chi_square_analysis(self, df1, df2,
                            bin_width: float,
                            time_column='time',
                            value_column='value'):
        import pandas as pd

        # binning the data
        def bin_data(df):
            b = ((df[time_column] // bin_width) * bin_width).astype(int)
            return df.groupby(b)[value_column].sum()

        b1 = bin_data(df1)
        b2 = bin_data(df2)
        all_bins = b1.index.union(b2.index)
        b1 = b1.reindex(all_bins, fill_value=0)
        b2 = b2.reindex(all_bins, fill_value=0)

        T1, T2 = b1.sum(), b2.sum()
        Tot = T1 + T2
        E1 = (b1 + b2) * (T1 / Tot)
        E2 = (b1 + b2) * (T2 / Tot)

        χ2_1 = ((b1 - E1)**2 / E1).replace([np.inf, np.nan], 0).sum()
        χ2_2 = ((b2 - E2)**2 / E2).replace([np.inf, np.nan], 0).sum()
        χ2_tot = χ2_1 + χ2_2

        ν = len(all_bins) - 1
        p = 1 - chi2.cdf(χ2_tot, ν)

        table = pd.DataFrame({
            'Time Bin': all_bins,
            'Obs1': b1.values,
            'Obs2': b2.values,
            'Exp1': E1.values,
            'Exp2': E2.values
        })
        return {
            'table': table,
            'chi2_1': χ2_1,
            'chi2_2': χ2_2,
            'chi2_total': χ2_tot,
            'dof': ν,
            'pvalue': p
        }

    # this function is used to perform a t-test analysis
    # it takes the data and the population mean as input and returns the t-test analysis
    def t_test_analysis(self, data: np.ndarray, popmean: float):
        tstat, p = ttest_1samp(data, popmean)
        conclusion = "reject H₀" if p < 0.05 else "fail to reject H₀"
        return {'tstat': tstat, 'pvalue': p, 'conclusion': conclusion}
