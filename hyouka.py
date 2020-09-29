import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeed
def hyouka(myStrategy):
	kabu = pd.read_csv("./kabu_data.csv")
	kabu["Date"] = pd.to_datetime(kabu["Date"])
	code_number = kabu.銘柄コード.unique()[:-1]
	kabu = kabu.set_index(["銘柄コード","Date"])

	cerebro = bt.Cerebro() # Cerebroエンジンをインスタンス化
	cerebro.addstrategy(myStrategy) # ストラテジーを追加
	for i in range(len(code_number)):
	    data = btfeed.PandasData(dataname=kabu.loc[code_number[i]][::-1]) # Cerebro形式にデータを変換
	    cerebro.adddata(data) # データをCerebroエンジンに追加
	cerebro.broker.setcash(1000000.0) # 所持金を設定
	cerebro.broker.setcommission(commission=0.0005) # 手数料（スプレッド）を0.05%に設定
	cerebro.addsizer(bt.sizers.PercentSizer, percents=50) # デフォルト（buy/sellで取引量を設定していない時）の取引量を所持金に対する割合で指定する
	startcash = cerebro.broker.getvalue() # 開始時の所持金
	cerebro.broker.set_coc(True) # 発注時の終値で約定する

	import backtrader.analyzers as btanalyzers # バックテストの解析用ライブラリ
	cerebro.addanalyzer(btanalyzers.DrawDown, _name='myDrawDown') # ドローダウン
	cerebro.addanalyzer(btanalyzers.SQN, _name='mySQN') # SQN
	cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='myTradeAnalyzer') # トレードの勝敗等の結果

	thestrats = cerebro.run() # バックテストを実行
	thestrat = thestrats[0] # 解析結果の取得
	return startcash + thestrat.analyzers.myTradeAnalyzer.get_analysis().pnl.net.total
