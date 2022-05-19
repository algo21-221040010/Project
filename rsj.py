from datetime import time

import numpy as np

from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager,
    OrderData,
    TradeData,
    StopOrder)
from vnpy.trader.object import (
    BarData,
    TickData
)


class RsjStrategy(CtaTemplate):
    """"""
    author = "Bili"

    # 定义参数
    rsj_window = 12

    # 定义变量
    rsj_value = 0.0

    parameters = [
        "rsj_window"
    ]
    variables = [
        "rsj_value"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.am = NewArrayManager()

    def on_init(self):
        """
        策略初始化
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        启动策略
        """
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        """
        策略停止
        """
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick: TickData):
        """
        TICK更新
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        K线更新
        """
        self.bg.update_bar(bar)

    def on_5min_bar(self, bar: BarData):
        """5分钟K线更新"""
        # 全撤委托
        self.cancel_all()

        # 缓存K线
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 计算技术指标
        self.rsj_value = self.am.rsj(self.rsj_window)

        # 判断交易信号
        if bar.datetime.time() == time(14, 50):
            if self.rsj_value > 0:
                if self.pos > 0:
                    self.sell(bar.close_price - 10, 1)

                self.short(bar.close_price - 10, 1)
            elif self.rsj_value < 0:
                if self.pos < 0:
                    self.cover(bar.close_price + 10, 1)

                self.buy(bar.close_price + 10, 1)

        # 更新图形界面
        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass


class NewArrayManager(ArrayManager):

    def __init__(self, size=100):
        """"""
        super().__init__(size)

        self.return_array: np.ndarray = np.zeros(size)

    def update_bar(self, bar: BarData) -> None:
        """更新K线"""
        # 先调用父类的方法，更新K线
        super().update_bar(bar)
        # 计算涨跌变化
        if not self.close_array[-2]:      # 如果尚未初始化上一根收盘价
            last_return = 0
        else:
            last_return = self.close_array[-1] / self.close_array[-2] - 1

        # 缓存涨跌变化
        self.return_array[:-1] = self.return_array[1:]
        self.return_array[-1] = last_return

    def rsj(self, n: int) -> float:
        """计算RSJ指标"""
        # 切片出要计算用的收益率数据
        return_data = self.return_array[-n:]

        # 计算RV
        rv = np.sum(pow(return_data, 2))

        # 计算RV +/-
        positive_data = np.array([r for r in return_data if r > 0])
        negative_data = np.array([r for r in return_data if r <= 0])

        rv_positive = np.sum(pow(positive_data, 2))
        rv_negative = np.sum(pow(negative_data, 2))

        # 计算RSJ
        rsj = (rv_positive - rv_negative) / rv
        return rsj