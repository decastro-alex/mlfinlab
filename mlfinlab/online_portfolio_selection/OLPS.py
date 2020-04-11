from mlfinlab.online_portfolio_selection.olps_utils import *


# General OLPS class
class OLPS(object):
    # Initialize
    def __init__(self):
        """
        :param weights: (pd.DataFrame) final weight of portfolio
        :param all_weights: (pd.DataFrame) all weights of portfolio
        :param portfolio_return: (pd.DataFrame) all returns of portfolio
        """
        # weights
        self.weights = None
        self.all_weights = None
        # delayed portfolio
        self.portfolio_start = None
        # asset names
        self.asset_name = None
        self.number_of_assets = None
        # asset time
        self.time = None
        self.number_of_time = None
        # final asset time
        self.final_time = None
        self.final_number_of_time = None
        # relative return and final relative return
        self.relative_return = None
        self.final_relative_return = None
        # portfolio return
        self.portfolio_return = None

        # self.asset_prices = None
        # self.covariance_matrix = None
        # self.portfolio_risk = None
        # self.portfolio_sharpe_ratio = None
        # self.expected_returns = None
        # self.returns_estimator = ReturnsEstimation()

    # public method idea
    # OLPS.allocate(some_data)
    # OLPS.weights
    # OLPS.summary()
    # OLPS.returns
    def allocate(self,
                 asset_prices,
                 weights=None,
                 portfolio_start=0,
                 resample_by=None):
        """
        :param asset_prices: (pd.Dataframe) a dataframe of historical asset prices (daily close)
        :param weights: any weights
        :param portfolio_start: (int) delay the portfolio by n number of time
        :param resample_by: (str) specifies how to resample the prices - weekly, daily, monthly etc.. Defaults to
                                  None for no resampling
        """
        # Data Check
            # Some sort of initial check to make sure data fits the standards
            # asset name in right format
            # asset price in right format
            # resample_by in right format
            # weights add up to 1
            # resample function
        # not implemented yet
        self.__check_asset(asset_prices, weights, portfolio_start, resample_by)

        # Data Prep
        self.__initialize(asset_prices, weights, portfolio_start, resample_by)

        # Actual weight calculation
        # For future portfolios only change __run() if we want to change it to batch style
        # or change __update_weight to change stepwise function
        # or change __first_weight if we delay our portfolio return start date
        self.__run(weights)

        # Calculate Portfolio Returns
        self.__calculate_returns(self.all_weights, self.final_relative_return)

        # convert everything to make presentable
        self.__conversion(_all_weights=self.all_weights, _portfolio_return=self.portfolio_return)

    # check for valid dataset
    # raise ValueError
    def __check_asset(self, _asset_prices, _weights, _portfolio_start, _resample_by):
        # is the dataset actually valid
        pass
        # check _asset_prices is dataframe
        # check weights size is _asset_prices column size
        # _resample_by actually works
        # _portfolio_start is a valid number

    def __initialize(self, _asset_prices, _weights, _portfolio_start, _resample_by):
        # resample asset
        if _resample_by is not None:
            _asset_prices = _asset_prices.resample(_resample_by).last()

        # set portfolio start
        self.portfolio_start = _portfolio_start

        # set asset names
        self.asset_name = _asset_prices.columns

        # set time
        self.time = _asset_prices.index

        # calculate number of assets
        self.number_of_assets = self.asset_name.size

        # calculate number of time
        self.number_of_time = self.time.size

        # calculate relative returns and final relative returns
        self.relative_return = self.__relative_return(_asset_prices)

        # set portfolio start
        self.portfolio_start = _portfolio_start

        # set final returns
        self.final_time = self.time[self.portfolio_start:]
        self.final_number_of_time = self.final_time.size
        self.final_relative_return = self.relative_return[self.portfolio_start:]

        # set final_weights
        self.all_weights = np.zeros((self.final_number_of_time, self.number_of_assets))

        # set portfolio_return
        self.portfolio_return = np.zeros((self.final_number_of_time, self.number_of_assets))

    # calculate relative returns
    def __relative_return(self, _asset_prices):
        # percent change of each row
        # first row is blank because no change, so make it 0
        # add 1 to all values so that the values can be multiplied easily
        # change to numpy array
        relative_return = np.array(_asset_prices.pct_change().fillna(0) + 1)
        return relative_return

    # for this one, it doesn't matter, but for subsequent complex selection problems, we might have to include a
    # separate run method for each iteration and not clog the allocate method.
    # after calculating the new weight add that to the all weights
    def __run(self, _weights):
        # set initial weights
        self.weights= self.__first_weight(_weights)
        self.all_weights[0] = self.weights

        # Run the Algorithm for the rest of data
        for t in range(1, self.final_number_of_time):
            # update weights
            new_weight = self.__update_weight(self.weights)
            self.all_weights[t] = new_weight

    # initialize first weight
    # might change depending on algorithm
    def __first_weight(self, _weights):
        if _weights is None:
            return self.__uniform_weight(self.number_of_assets)
        else:
            return _weights

    # return uniform weights numpy array (1/n, 1/n, 1/n ...)
    def __uniform_weight(self, n):
        return np.ones(n) / n

    # for the first one, just return the same weight
    # only have to change this for future iteration
    def __update_weight(self, _weights):
        return _weights

    # calculate portfolio returns
    def __calculate_returns(self, _all_weights, _relative_return):
        self.portfolio_return = np.diagonal(np.dot(_relative_return, _all_weights.T)).cumprod()

    # method to normalize sum of weights to 1
    def __normalize(self, _weights):
        return _weights / np.sum(_weights)

    # method to get a diagonal multiplication of two arrays
    # equivalent to np.diag(np.dot(A, B))
    def __diag_mul(self, A, B):
        return (A * B.T).sum(-1)

    def __conversion(self, _all_weights, _portfolio_return):
        self.all_weights = pd.DataFrame(_all_weights, index=self.final_time, columns=self.asset_name)
        self.portfolio_return = pd.DataFrame(_portfolio_return, index=self.final_time, columns=["Returns"])

    # calculate the variance based on the price
    def volatility(self):
        pass

    # Calculate Sharpe Ratio
    def sharpe_ratio(self):
        # self.portfolio_sharpe_ratio = ((self.portfolio_return - risk_free_rate) / (self.portfolio_risk ** 0.5))
        pass

    # return maximum drawdown
    def maximum_drawdown(self):
        return min(self.portfolio_return)

    # return summary of the portfolio
    def summary(self):
        pass


def main():
    stock_price = pd.read_csv("../tests/test_data/stock_prices.csv", parse_dates=True, index_col='Date')
    stock_price = stock_price.dropna(axis=1)
    initial_portfolio = OLPS()
    initial_portfolio.allocate(stock_price)
    print(initial_portfolio.all_weights)
    print(initial_portfolio.portfolio_return)
    initial_portfolio.portfolio_return.plot()


if __name__ == "__main__":
    main()