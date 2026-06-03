"""
AKShare 数据采集客户端
负责从AKShare获取A股行情和K线数据
"""
import akshare as ak
import pandas as pd
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AkshareClient:
    """AKShare数据采集客户端"""
    
    def __init__(self):
        self.name = "AKShare"
    
    def get_quote(self, code: str) -> Optional[Dict[str, Any]]:
        """
        获取单只股票实时行情
        
        Args:
            code: 股票代码，如 "000001"
            
        Returns:
            行情字典，失败返回None
        """
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == code]
            if row.empty:
                logger.warning(f"股票 {code} 不存在")
                return None
            
            data = row.iloc[0]
            return {
                'code': str(data['代码']),
                'name': str(data['名称']),
                'price': float(data['最新价']),
                'change_pct': float(data['涨跌幅']),
                'change_amount': float(data['涨跌额']),
                'volume': float(data['成交量']),
                'turnover': float(data['成交额']),
                'high': float(data['最高']),
                'low': float(data['最低']),
                'open': float(data['今开']),
                'close_prev': float(data['昨收']),
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"获取股票 {code} 行情失败: {e}")
            return None
    
    def get_realtime_quotes(self, codes: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取实时行情
        
        Args:
            codes: 股票代码列表
            
        Returns:
            行情字典列表
        """
        results = []
        try:
            df = ak.stock_zh_a_spot_em()
            for code in codes:
                row = df[df['代码'] == code]
                if row.empty:
                    logger.warning(f"股票 {code} 不存在，跳过")
                    continue
                    
                data = row.iloc[0]
                results.append({
                    'code': str(data['代码']),
                    'name': str(data['名称']),
                    'price': float(data['最新价']),
                    'change_pct': float(data['涨跌幅']),
                    'volume': float(data['成交量']),
                    'high': float(data['最高']),
                    'low': float(data['最低']),
                    'timestamp': datetime.now()
                })
        except Exception as e:
            logger.error(f"批量获取行情失败: {e}")
        
        return results
    
    def get_kline(self, code: str, period: str = "daily", 
                   start_date: Optional[str] = None, 
                   end_date: Optional[str] = None,
                   adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        获取K线历史数据
        
        Args:
            code: 股票代码，如 "000001"
            period: K线周期 "daily"/"weekly"/"monthly"
            start_date: 开始日期 "YYYYMMDD"
            end_date: 结束日期 "YYYYMMDD"
            adjust: 复权类型 "qfq"(前复权)/"hfq"(后复权)/""(不复权)
            
        Returns:
            K线DataFrame，失败返回None
        """
        try:
            # 默认获取近一年数据
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            
            df = ak.stock_zh_a_hist(
                symbol=code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'turnover',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change_amount',
                '换手率': 'turnover_rate'
            })
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {code} K线失败: {e}")
            return None
    
    def get_intraday(self, code: str) -> Optional[pd.DataFrame]:
        """
        获取分时数据
        
        Args:
            code: 股票代码
            
        Returns:
            分时DataFrame
        """
        try:
            df = ak.stock_zh_a_minute(symbol=code, period='1', adjust='')
            return df
        except Exception as e:
            logger.error(f"获取股票 {code} 分时数据失败: {e}")
            return None
    
    def get_stock_info(self, code: str) -> Optional[Dict[str, Any]]:
        """
        获取个股基本信息
        
        Args:
            code: 股票代码
            
        Returns:
            基本信息字典
        """
        try:
            df = ak.stock_individual_info_em(symbol=code)
            info = dict(zip(df['item'], df['value']))
            return info
        except Exception as e:
            logger.error(f"获取股票 {code} 基本信息失败: {e}")
            return None
