#Visualizer class 
class Visualizer:
    def __init__(self, stock):
        self._stock_obj = stock 
        self._data = stock.data
        self._ticker = stock.ticker 


    def plot_indicators(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        try:
            ax1.plot(self._data.index,self._data["Close"],label="Price")
            ax1.plot(self._data.index,self._data["SMA"],label="SMA")
            ax1.plot(self._data.index,self._data["EMA"],label="EMA")
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
