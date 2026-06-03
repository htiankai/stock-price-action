"""
K线图表模块
使用Plotly绑制K线图和技术指标
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Tuple


class ChartRenderer:
    """K线图表渲染器"""
    
    def __init__(self):
        self.up_color = '#26a69a'      # 上涨绿色
        self.down_color = '#ef5350'     # 下跌红色
        self.volume_up_color = 'rgba(38, 166, 154, 0.5)'
        self.volume_down_color = 'rgba(239, 83, 80, 0.5)'
    
    def render_candlestick(self, df: pd.DataFrame, 
                          title: str = "K线走势",
                          show_volume: bool = True) -> go.Figure:
        """
        渲染K线图表
        
        Args:
            df: K线数据，必须包含 open/high/low/close/date 列
            title: 图表标题
            show_volume: 是否显示成交量
            
        Returns:
            Plotly Figure对象
        """
        if show_volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=('', '成交量')
            )
        else:
            fig = go.Figure()
        
        # 判断涨跌
        df = df.copy()
        df['is_up'] = df['close'] >= df['open']
        
        # K线蜡烛图
        fig.add_trace(
            go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='K线',
                increasing_line_color=self.up_color,
                decreasing_line_color=self.down_color,
                increasing_fillcolor=self.up_color,
                decreasing_fillcolor=self.down_color
            ),
            row=1 if show_volume else None,
            col=1
        )
        
        # 成交量柱状图
        if show_volume:
            colors = [self.volume_up_color if is_up else self.volume_down_color 
                     for is_up in df['is_up']]
            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name='成交量',
                    marker_color=colors,
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # 布局设置
        fig.update_layout(
            title=title,
            xaxis_rangeslider_visible=False,
            template='plotly_white',
            height=600,
            margin=dict(l=60, r=60, t=60, b=60),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        # 更新x轴
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"])  # 隐藏周末
            ],
            row=1 if show_volume else None,
            col=1
        )
        
        return fig
    
    def add_ma(self, fig: go.Figure, df: pd.DataFrame, 
               periods: List[int] = [5, 10, 20, 60]) -> go.Figure:
        """
        添加均线
        
        Args:
            fig: 图表对象
            df: K线数据
            periods: 均线周期列表
            
        Returns:
            更新后的Figure
        """
        colors = ['#2196F3', '#FF9800', '#9C27B0', '#4CAF50']
        
        for i, period in enumerate(periods):
            if f'ma{period}' not in df.columns:
                df[f'ma{period}'] = df['close'].rolling(window=period).mean()
            
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df[f'ma{period}'],
                    mode='lines',
                    name=f'MA{period}',
                    line=dict(color=colors[i % len(colors)], width=1.5)
                ),
                row=1, col=1
            )
        
        return fig
    
    def add_bollinger_bands(self, fig: go.Figure, df: pd.DataFrame,
                           period: int = 20, std_dev: float = 2.0) -> go.Figure:
        """
        添加布林带
        
        Args:
            fig: 图表对象
            df: K线数据
            period: 周期
            std_dev: 标准差倍数
        """
        df = df.copy()
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        df['bb_std'] = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + std_dev * df['bb_std']
        df['bb_lower'] = df['bb_middle'] - std_dev * df['bb_std']
        
        # 上轨
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['bb_upper'],
                mode='lines', name='BB上轨',
                line=dict(color='rgba(156, 39, 176, 0.5)', width=1),
                showlegend=True
            ),
            row=1, col=1
        )
        
        # 下轨
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['bb_lower'],
                mode='lines', name='BB下轨',
                line=dict(color='rgba(156, 39, 176, 0.5)', width=1),
                fill='tonexty',
                fillcolor='rgba(156, 39, 176, 0.1)',
                showlegend=True
            ),
            row=1, col=1
        )
        
        # 中轨
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['bb_middle'],
                mode='lines', name='BB中轨',
                line=dict(color='rgba(156, 39, 176, 0.5)', width=1, dash='dash'),
                showlegend=False
            ),
            row=1, col=1
        )
        
        return fig
    
    def add_macd(self, fig: go.Figure, df: pd.DataFrame,
                 fast: int = 12, slow: int = 26, signal: int = 9) -> go.Figure:
        """
        添加MACD副图
        
        Args:
            fig: 图表对象
            df: K线数据
            fast/slow/signal: MACD参数
        """
        # 计算MACD
        df = df.copy()
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # 创建新的子图
        # 暂时添加为独立trace，需要时可以通过update_layout扩展
        colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df['macd_hist']]
        
        # MACD主图
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['macd'],
                mode='lines', name='MACD',
                line=dict(color='#2196F3', width=1.5)
            ),
            row=3, col=1
        )
        
        # MACD信号线
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['macd_signal'],
                mode='lines', name='Signal',
                line=dict(color='#FF9800', width=1.5)
            ),
            row=3, col=1
        )
        
        # MACD柱状图
        fig.add_trace(
            go.Bar(
                x=df['date'], y=df['macd_hist'],
                name='Histogram',
                marker_color=colors,
                showlegend=False
            ),
            row=3, col=1
        )
        
        return fig
    
    def add_rsi(self, fig: go.Figure, df: pd.DataFrame, period: int = 14) -> go.Figure:
        """
        添加RSI副图
        
        Args:
            fig: 图表对象
            df: K线数据
            period: RSI周期
        """
        df = df.copy()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # RSI线
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['rsi'],
                mode='lines', name=f'RSI({period})',
                line=dict(color='#9C27B0', width=1.5)
            ),
            row=4, col=1
        )
        
        # 超买超卖线
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="超买", row=4, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                     annotation_text="超卖", row=4, col=1)
        
        return df[['date', 'rsi']]  # 返回RSI数据供后续使用
