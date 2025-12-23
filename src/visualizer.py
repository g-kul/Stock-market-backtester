import matplotlib.pyplot as plt 


#Visualizer class 
class Visualizer:
    def __init__(self, stock):
        self._stock_obj = stock 
        self._data = stock.data
        self._ticker = stock.ticker 


    def plot_indicators(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

        try:
            ax1.plot(self._data.index,self._data["Close"],label="Price")
            ax1.plot(self._data.index,self._data["Short_SMA"],label="Short_SMA")
            ax1.plot(self._data.index,self._data["Long_SMA"],label="Long_SMA")
            ax1.plot(self._data.index,self._data["Short_EMA"],label="Short_EMA")
            ax1.plot(self._data.index,self._data["Long_EMA"],label="Long_EMA")
            ax1.set_ylabel("Price")
            ax1.legend()
            ax1.set_title(f"{self._ticker} Price and Indicators ")

            ax2.plot(self._data.index,self._data["RSI"],color="purple")
            ax2.axhline(70, color="red",linestyle="--",label="Overbought")
            ax2.axhline(30, color="green",linestyle="--",label="Oversold")
            ax2.set_ylabel("RSI")
            ax2.set_ylim(0, 100)
            ax2.legend()

            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error: {e})


    def plot_signals(self,strategy):
        fig,ax = plt.subplots(figsize=(14,8))
        
        try:
            ax.plot(self._data.index, self._data["Close"],label="Close Price",linewidth=2)
            if isinstance(strategy, MAC_S):
                signal_col = "MAC_Signal"
            elif isinstance(strategy, RSI_S):
                signal_col = "RSI_Signal"
            elif isinstance(strategy, COMBINED_S):
                signal_col = "COMB_Signal"
            buy_signals = df[self._data[signal_col] == 1]
            ax.scatter(buy_signals.index, buy_signals["Close"],
                       marker='^',color="green",s=100,label="Buy Signal",zorder=5)
            sell_signals = df[self.data[signal_col] == -1]
            ax.scatter(sell_signals.index, sell_signals["Close"],
                       marker='^',color="green",s=100,label="Sell Signal",zorder=5)
            ax.set_xlabel("Data")
            ax.set_ylabel("Price")
            ax.set_title(f"Signals plot - {self._ticker}")
            ax.legend()
            ax.grid(True,alpha=0.3)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error: {e}")


    def plot_portfolio_performance(self,backtest):
        backtest_results = backtest.get_results()
        portfolio_history = backtest_results['Porfolio history']
        dates = [x[0] for x in portfolio_history]
        values = [x[1] for x in portfolio_history]

        fig,ax = plt.subplots(figsize=(14,8))

        try:
            ax.plot(dates,values,linewidth=2,label="Portfolio Value")
            ax.axline(y=backtest_results['Initial cash'],
                      color="gray",linestyle='--',label="Initial Cash")
            ax.set_xlabel("Date")
            ax.set_ylabel("Portfolio Value ($)")
            ax.set_title(f"Portfolio performance - {self._ticker}")
            ax.legend()
            ax.grid(True,alpha=0.3)

            textstr = f"Initial: {backtest_results['Initial cash']:.2f}\n"
            textstr = f"Final: {backtest_results['Final total cash']:.2f}\n"
            textstr = f"Return: {backtest_results['Total returns']:.2f}\n"
            textstr = f"Trades: {backtest_results['No of trades']:.2f}\n"

            props = dic(boxstyle='round',facecolor="wheat",alpha=0.5)
            ax.text(0.05,0.95,textstr,transform=ax.transAxes,fontsize=10,
                    verticalalignment='top',bbox=props)
            plt.tight_layout()
            plt.show()
        
        except Exception as e:
            print(f"Error: {e}")


    def compare_strategies(self, results_dict):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Portfolio values over time
        for strategy_name, results in results_dict.items():
            history = results['Portfolio history']
            dates = [x[0] for x in history]
            values = [x[1] for x in history]
            ax1.plot(dates, values, label=strategy_name, linewidth=2)
        
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.set_title('Strategy Comparison - Portfolio Growth')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Bar chart of returns
        strategy_names = list(results_dict.keys())
        returns = [results_dict[name]['Total returns'] for name in strategy_names]
        
        colors = ['green' if r > 0 else 'red' for r in returns]
        ax2.bar(strategy_names, returns, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_ylabel('Return (%)')
        ax2.set_title('Strategy Comparison - Total Returns')
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()


    def plot_ml_predictions(self,ml_df):
        fig,(ax1,ax2) = plt.subplots(2,1,figsize=(14,10))

        try:
            ax1.plot(ml_df.index, ml_df['Close'], label="Actual Price",linewidth=2)
            up_days = df[ml_df["ML_Signal"] > 0]
            ax1.scatter(up_days.index,up_days["Close"],
                        color="green",alpha=0.3,s=20,label="Predicted Up")

            down_days = df[ml_df["ML_Signal"] < 0]
            ax1.scatter(down_days.index,down_days["Close"],
                        color="red",alpha=0.3,s=20,label="Predicted Down")
            ax1.set_ylabel("Price")
            ax1.set_title(f"ML Prediction - {self._ticker}")
            ax1.legend()
            ax1.grid(True,alpha=0.3)

            #Plot-2 predicted values
            ax2.plot(ml_df.index, ml_df['ML_Prediction'], label="Predicted Price",color="purple",linewidth=1.5)
            ax2.axline(y=0,color='black',linestyle='-',linewidth=0.5)
            ax2.fill_between(ml_df.index,0,ml_df['ML_Signal'],
                             where(ml_df['ML_Signal'] > 0), color="green",alpha=0.3)
            ax2.fill_between(ml_df.index,0,ml_df['ML_Signal'],
                             where(ml_df['ML_Signal'] < 0), color="red",alpha=0.3)
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Predicted Return")
            ax2.set_title(f"ML Predicted Returns")
            ax2.grid(True,alpha=0.3)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error: {e}")
        




        

