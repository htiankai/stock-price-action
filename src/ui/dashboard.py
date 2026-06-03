"""
Streamlit 仪表盘主模块
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.data.akshare_client import AkshareClient
from src.data.data_cache import DataCache, ConfigManager
from src.ui.chart import ChartRenderer

# 页面配置
st.set_page_config(
    page_title="A股价格行为分析",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化组件
@st.cache_resource
def get_clients():
    return AkshareClient(), DataCache(), ConfigManager()

akshare_client, data_cache, config_manager = get_clients()
chart_renderer = ChartRenderer()


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("📈 自选股")
        
        # 加载自选股
        watchlist = config_manager.load_stocks()
        
        # 股票选择
        if watchlist:
            stock_options = {s['name']: s['code'] for s in watchlist}
            selected_name = st.selectbox("选择股票", list(stock_options.keys()))
            selected_code = stock_options[selected_name]
        else:
            st.info("自选股列表为空，请添加股票")
            selected_code = None
        
        # 添加股票
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            new_code = st.text_input("代码", placeholder="000001")
        with col2:
            new_name = st.text_input("名称", placeholder="平安银行")
        
        if st.button("添加", use_container_width=True):
            if new_code and new_name:
                # 自动判断市场
                market = "sh" if new_code.startswith(('6', '5')) else "sz"
                if config_manager.add_stock(new_code, new_name, market):
                    st.success(f"已添加 {new_name}")
                    st.rerun()
                else:
                    st.error("添加失败")
        
        # 删除股票
        if selected_code and st.button("删除", use_container_width=True):
            if config_manager.remove_stock(selected_code):
                st.success("已删除")
                st.rerun()
        
        # K线周期
        st.divider()
        period = st.radio(
            "K线周期",
            ["日K", "周K", "月K"],
            horizontal=True,
            index=0
        )
        period_map = {"日K": "daily", "周K": "weekly", "月K": "monthly"}
        
        # 设置
        st.divider()
        with st.expander("设置"):
            show_ma = st.checkbox("显示均线", value=True)
            show_bb = st.checkbox("显示布林带", value=False)
            show_volume = st.checkbox("显示成交量", value=True)
        
        return selected_code, period_map[period], {
            'show_ma': show_ma,
            'show_bb': show_bb,
            'show_volume': show_volume
        }


def render_quote_panel(code: str):
    """渲染行情面板"""
    quote = akshare_client.get_quote(code)
    
    if quote:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label=quote['name'],
                value=f"{quote['price']:.2f}",
                delta=f"{quote['change_pct']:.2f}%"
            )
        
        with col2:
            st.metric("今开", f"{quote['open']:.2f}")
        
        with col3:
            st.metric("最高", f"{quote['high']:.2f}")
        
        with col4:
            st.metric("最低", f"{quote['low']:.2f}")
        
        with col5:
            st.metric("成交量", f"{quote['volume']/10000:.2f}万")
    else:
        st.error("获取行情失败")


def render_kline_chart(code: str, period: str, settings: dict):
    """渲染K线图表"""
    with st.spinner("加载K线数据..."):
        df = akshare_client.get_kline(code, period=period, adjust="qfq")
        
        if df is not None and not df.empty:
            # 创建图表
            fig = chart_renderer.render_candlestick(
                df,
                title=f"K线走势 - {period}",
                show_volume=settings['show_volume']
            )
            
            # 添加均线
            if settings['show_ma']:
                fig = chart_renderer.add_ma(fig, df)
            
            # 添加布林带
            if settings['show_bb']:
                fig = chart_renderer.add_bollinger_bands(fig, df)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("获取K线数据失败")


def render_analysis_panel(code: str):
    """渲染分析面板"""
    st.subheader("📊 技术指标")
    
    # 获取K线数据
    df = akshare_client.get_kline(code, period="daily", adjust="qfq")
    
    if df is not None and not df.empty:
        col1, col2, col3 = st.columns(3)
        
        # MA指标
        with col1:
            ma5 = df['close'].iloc[-5:].mean()
            ma10 = df['close'].iloc[-10:].mean()
            ma20 = df['close'].iloc[-20:].mean()
            st.write("**均线**")
            st.write(f"MA5: {ma5:.2f}")
            st.write(f"MA10: {ma10:.2f}")
            st.write(f"MA20: {ma20:.2f}")
        
        # 涨跌统计
        with col2:
            change = df['close'].iloc[-1] - df['close'].iloc[-2]
            change_pct = (change / df['close'].iloc[-2]) * 100
            volume_avg = df['volume'].iloc[-5:].mean()
            st.write("**涨跌**")
            st.write(f"今日涨跌: {change:.2f} ({change_pct:.2f}%)")
            st.write(f"量能: {'放量' if df['volume'].iloc[-1] > volume_avg else '缩量'}")
        
        # 支撑阻力
        with col3:
            high_20 = df['high'].iloc[-20:].max()
            low_20 = df['low'].iloc[-20:].min()
            current = df['close'].iloc[-1]
            st.write("**支撑/阻力**")
            st.write(f"20日高: {high_20:.2f}")
            st.write(f"20日低: {low_20:.2f}")
            st.write(f"当前位置: {(current - low_20)/(high_20 - low_20)*100:.1f}%")
    else:
        st.info("暂无数据")


def main():
    """主函数"""
    # 渲染侧边栏
    selected_code, period, chart_settings = render_sidebar()
    
    if selected_code:
        # 行情面板
        render_quote_panel(selected_code)
        
        # K线图表
        render_kline_chart(selected_code, period, chart_settings)
        
        # 分析面板
        with st.container():
            render_analysis_panel(selected_code)
    else:
        # 空状态
        st.title("📈 A股价格行为分析系统")
        st.info("👈 请先在侧边栏添加自选股")
        
        # 显示系统说明
        with st.expander("系统说明"):
            st.write("""
            **功能特性：**
            - 实时行情监控
            - K线图表分析（支持日/周/月线）
            - 技术指标（均线、布林带）
            - 支撑阻力分析
            
            **使用方法：**
            1. 在左侧添加自选股
            2. 选择要查看的股票
            3. 设置K线周期和显示选项
            """)


if __name__ == "__main__":
    main()
