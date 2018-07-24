import urllib.request,webbrowser

tickers = ['AAPL']
listOfStocks = []

class Stock():
    def __init__(self,symbol,price,dividendYield,dividendPerShare,earningsPerShare,PERatio,marketCap):
        self.symbol = symbol
        self.price = price
        self.dividendYield = dividendYield
        self.dividendPerShare = dividendPerShare
        self.earningsPerShare = earningsPerShare
        self.marketCap = marketCap
        try:
            self.payoutRatio = round((((self.dividendYield/100)*self.price)/self.earningsPerShare)*10000)/100
        except:
            self.payoutRatio = "N/A"
        self.PERatio = PERatio
    def Display(self):
        print ("")
        print ("Symbol:",self.symbol)
        print ("Price: $",self.price)
        print ("Yield:",self.dividendYield,"%")
        print ("Dividend Per Share:",self.dividendPerShare)
        print ("Earnings Per Share:",self.earningsPerShare)
        print ("Payout Ratio:",self.payoutRatio,"%")
        print ("P/E:",self.PERatio)
        print ("Market Cap:",self.marketCap)
        print ("Website: https://www.google.com/finance?q=" + self.symbol)
#https://finance.yahoo.com/quote/AAPL
def DownloadData(url):
    #html = urllib.request.urlopen(url)
    #html = html.readlines()
    with urllib.request.urlopen(url) as response:
         html = response.readlines()
    #print (html)
    return html

def FindPatternInData(pattern,data):
    listOfValues = []
    for l in data:
        val = ""
        for i in range(len(l)):
            if i >= len(pattern):
                val += l[i]
            elif i < len(pattern) and l[i] != pattern[i]:
                break
        if val != "":
            listOfValues.append(val[:-1])
    return listOfValues

def CreateStockClass(symbol, values):
    try:
        price = float(values[0].split(" - ")[1])
    except:
        price = "N/A"
    try:
        dividendYield = float(values[6].split("/")[1])
    except:
        dividendYield = "N/A"
    try:
        dividendPerShare = float(values[6].split("/")[0])
    except:
        dividendPerShare = "N/A"
    try:
        earningsPerShare = float(values[7])
    except:
        earningsPerShare = "N/A"
    try:
        PERatio = float(values[5])
    except:
        PERatio = "N/A"
    try:
        marketCap = values[4]
    except:
        marketCap = "N/A"

    temp = Stock(symbol,price,dividendYield,dividendPerShare,earningsPerShare,PERatio,marketCap)
    return temp
if __name__ == "__main__": 
    i = 0
    for t in tickers:
        i += 1
        print ("Downloading... " + t)
        print ("[" + str(i) + "/" + str(len(tickers)) + "]")
        # s = CreateStockClass(t,FindPatternInData('<td class="iyjjgb">',DownloadData("https://www.google.com/finance?q=" + t)))
        # listOfStocks.append(s)
        s = CreateStockClass(t,FindPatternInData('<span class="Trsdu(0.3s) ">',DownloadData("https://finance.yahoo.com/quote/" + t)))
        listOfStocks.append(s)

    j = 0
    valuableStocks = []
    for s in listOfStocks:
        if s.dividendYield >= 4 and s.earningsPerShare > 0 and s.PERatio > 10 and s.PERatio < 25 and s.payoutRatio < 100 and s.marketCap[len(s.marketCap)-1:] == "B":
            j += 1
            valuableStocks.append(s.symbol)
            s.Display()
            webbrowser.open("https://www.google.com/finance?q=" + s.symbol)

    print ("")
    print (str(j),"results.\n")
    print (valuableStocks)