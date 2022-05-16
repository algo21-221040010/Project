import asyncio
from typing import Optional, Union


class Twap(object):
    """
    Twap 算法实现了在设定的交易时间段内，完成设定的下单手数。
    构造 Twap 类的实例，该算法实例就会开始运行，根据以下逻辑下单：
    1. 将用户设置的总手数，拆分为一个随机手数列表，列表的值即为每次下单的手数，列表元素之和为总下单手数，同时每次下单手数也符合用户设置的每次下单手数的上下限；
    2. 将总的交易时间段拆分为随机时间间隔列表，列表的值即为每次下单的时间间隔，这些时间间隔相加应该等于总的下单时间；
    3. 每一次下单，在两个列表中分别取出下单手数、下单预计完成的时间，先用跟盘价下单，在当前时间间隔已经过去 2/3 或者只剩下 2s 时，主动撤掉未成交单，用对手价下单剩余手数；
    4. 在当前时间段已结束并且下单手数全部成交完，会开始下一次下单，重复第 3 步。
    基于以上逻辑，用户参数应该满足：
    平均每次下单时间 = duration / 下单次数 > 3s
    其中，下单次数 = 总的下单手数 / 平均每次下单手数 = 总的下单手数 / ((单次委托单最小下单手数 + 单次委托单最大下单手数) / 2)
    **注意**：
    时间段 duration，以 s 为单位，时长可以跨非交易时间段，但是不可以跨交易日。
    如果当前行情时间是 2020-09-15 09:10:00，那么下单的时间应该在 2020-09-15 09:10:00 ～ 2020-09-15 09:30:00；
    本模块不支持在回测中使用。
    """
    def __init__(self, symbol: str, direction: str, offset: str, volume: int, duration: float,
                 min_volume_each_order: int, max_volume_each_order: int, account = None):
        """
        创建 Twap 实例
        Args:
            symbol (str): 拟下单的合约symbol, 格式为 交易所代码.合约代码,  例如 "SHFE.cu1801"
            direction (str): "BUY" 或 "SELL"
            offset (str): "OPEN", "CLOSE"，"CLOSETODAY"
            volume (int): 需要下单的总手数
            duration (int): 算法执行的时长，以秒为单位，时长可以跨非交易时间段，但是不可以跨交易日
            * 设置为 60*10, 可以是 10:10～10:15 + 10:30~10:35
            min_volume_each_order (int):单笔最小委托单，每笔委托单数默认在最小和最大值中产生
            max_volume_each_order (int):单笔最大委托单，每笔委托单数默认在最小和最大值中产生
            account: [可选]指定发送下单指令的账户实例, 多账户模式下，该参数必须指定
        """
        self._account = account
        if self._account is None:
            raise Exception(f"多账户模式下, 需要指定账户实例 account")
        self._symbol = symbol
        self._direction = direction
        self._offset = offset
        self._volume = int(volume)
        self._duration = duration
        self._min_volume_each_order = int(min_volume_each_order)
        self._max_volume_each_order = int(max_volume_each_order)
        # 得到有效的手数序列和时间间隔序列
        volume_list, interval_list = self._get_volume_list()
        self._task = self._api.create_task(self._run(volume_list, interval_list))
        self._order_task = None

        self.trades = []  # 所有的 trade 列表
        self._trade_sum_volume = 0  # 所有 trade 的成交的总手数
        self._trade_sum_amount = 0  # 所有 trade 的成交的总支出 （手数*价格）
        self._trade_objs_chan = TqChan(self._api)
        self._trade_recv_task = self._api.create_task(self._trade_recv())

    def average_trade_price(self):
        # 平均成交价格
        if self._trade_sum_volume == 0:
            return float('nan')
        else:
            return self._trade_sum_amount / self._trade_sum_volume
    
    def buy():
        # 按 tick buy
        pass
    
    def sell():
        # 按 tick sell
        pass