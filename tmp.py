import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeed

class myStrategy(bt.Strategy): # ストラテジー
    
    n1 = 10 # 終値のSMA（単純移動平均）の期間
    n2 = 30 # 終値のSMA（単純移動平均）の期間

    def log(self, txt, dt=None, doprint=False): # ログ出力用のメソッド
        if doprint:
            print('{0:%Y-%m-%d %H:%M:%S}, {1}'.format(
                dt or self.datas[0].datetime.datetime(0),
                txt
            ))

    def __init__(self): # 事前処理
        # self.datas[0],self.datas[1]と複数のデータが格納されている
        self.sma1 = bt.indicators.SMA(self.datas[0].close, period=self.n1) # SMA（単純移動平均）のインジケータを追加
        self.sma2 = bt.indicators.SMA(self.datas[0].close, period=self.n2) # SMA（単純移動平均）のインジケータを追加
        self.crossover = bt.indicators.CrossOver(self.sma1, self.sma2) # sma1がsma2を上回った時に1、下回ったときに-1を返す
        self.sma3 = bt.indicators.SMA(self.datas[1].close, period=self.n1) # SMA（単純移動平均）のインジケータを追加
        self.sma4 = bt.indicators.SMA(self.datas[1].close, period=self.n2) # SMA（単純移動平均）のインジケータを追加
        self.crossover2 = bt.indicators.CrossOver(self.sma3, self.sma4) # sma3がsma4を上回った時に1、下回ったときに-1を返す        
    def next(self): # 行ごとに呼び出される
        #print(self.datas[0].volume.get()) これでpandasの値を取得
        # array('d', [1579740.0]) という形式
        cash = self.broker.getcash() #現金
        value = self.broker.getvalue() #純資産
        if self.position:
            pass
            #print(cash,value)
            #print(self.position) #株のポジション
            #print(self.getposition(self.datas[0], self.broker).size,self.getposition(self.datas[1], self.broker).size)
        
        # datas[0]の処理
        if self.crossover > 0: # SMA1がSMA2を上回った場合
            if self.position: # ポジションを持っている場合
                self.close(self.datas[0]) # ポジションをクローズする
            else:
                self.buy(self.datas[0],100) # 買い発注 何も指定なしなら半分の資産
        elif self.crossover < 0: # SMA1がSMA2を下回った場合
            if self.position: # ポジションを持っている場合
                self.close(self.datas[0]) # ポジションをクローズする

        # datas[1]の処理
        if self.crossover2 > 0: # SMA3がSMA4を上回った場合
            if self.position: # ポジションを持っている場合
                self.close(self.datas[1]) # ポジションをクローズする
            else:
                self.buy(self.datas[1],100) # 買い発注 何も指定なしなら半分の資産
        elif self.crossover2 < 0: # SMA3がSMA4を下回った場合
            if self.position: # ポジションを持っている場合
                self.close(self.datas[1]) # ポジションをクローズする
            
    def notify_order(self, order): # 注文のステータスの変更を通知する
        if order.status in [order.Submitted, order.Accepted]: # 注文の状態が送信済or受理済の場合
            return # 何もしない
        
        if order.status in [order.Completed]: # 注文の状態が完了済の場合
            if order.isbuy(): # 買い注文の場合
                self.log('買い約定, 取引量:{0:.2f}, 価格:{1:.2f}, 取引額:{2:.2f}, 手数料:{3:.2f},純資産:{4:.2f}'.format(
                        order.executed.size, # 取引量
                        order.executed.price, # 価格
                        order.executed.value, # 取引額
                        order.executed.comm, # 手数料
                        self.broker.getvalue() #純資産
                    ), 
                    dt=bt.num2date(order.executed.dt), # 約定の日時をdatetime型に変換
                    doprint=True # Trueの場合出力
                )
            elif order.issell(): # 売り注文の場合
                self.log('売り約定, 取引量:{0:.2f}, 価格:{1:.2f}, 取引額:{2:.2f}, 手数料:{3:.2f},純資産:{4:.2f}'.format(
                        order.executed.size, # 取引量
                        order.executed.price, # 価格
                        order.executed.value, # 取引額
                        order.executed.comm, # 手数料
                        self.broker.getvalue() #純資産
                    ), 
                    dt=bt.num2date(order.executed.dt), # 約定の日時をdatetime型に変換
                    doprint=True # Trueの場合ログを出力する
                )
                
        # 注文の状態がキャンセル済・マージンコール（証拠金不足）・拒否済の場合
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('注文 キャンセル・マージンコール（証拠金不足）・拒否',
                doprint=True
            )

    def notify_trade(self, trade): # 取引の開始/更新/終了を通知する
        if trade.isclosed: # トレードが完了した場合
            self.log('取引損益, 総額:{0:.2f}, 純額:{1:.2f}'.format(
                    trade.pnl, # 損益
                    trade.pnlcomm # 手数料を差し引いた損益
                ),
                doprint=True # Trueの場合ログを出力する
            )
