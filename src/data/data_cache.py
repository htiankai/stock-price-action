"""
数据缓存模块
负责管理数据缓存，提升访问效率
"""
import pandas as pd
import os
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class DataCache:
    """数据缓存管理器"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存有效期配置（秒）
        self.ttl = {
            'quote': 5,        # 实时行情5秒
            'intraday': 10,    # 分时数据10秒
            'kline_daily': 86400,  # 日K线1天
            'kline_minute': 60,    # 分钟K线1分钟
        }
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{key}.parquet"
    
    def _is_valid(self, cache_path: Path, ttl: int) -> bool:
        """检查缓存是否有效"""
        if not cache_path.exists():
            return False
        
        # 检查文件修改时间
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = (datetime.now() - mtime).total_seconds()
        return age < ttl
    
    def get(self, key: str, cache_type: str = 'quote') -> Optional[pd.DataFrame]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            cache_type: 缓存类型，决定TTL
            
        Returns:
            缓存的DataFrame，无效返回None
        """
        cache_path = self._get_cache_path(key)
        ttl = self.ttl.get(cache_type, 60)
        
        if not self._is_valid(cache_path, ttl):
            return None
        
        try:
            df = pd.read_parquet(cache_path)
            logger.debug(f"缓存命中: {key}")
            return df
        except Exception as e:
            logger.warning(f"读取缓存失败 {key}: {e}")
            return None
    
    def set(self, key: str, df: pd.DataFrame) -> bool:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            df: 要缓存的DataFrame
            
        Returns:
            是否成功
        """
        cache_path = self._get_cache_path(key)
        try:
            df.to_parquet(cache_path, index=False)
            logger.debug(f"缓存写入: {key}")
            return True
        except Exception as e:
            logger.warning(f"写入缓存失败 {key}: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """删除指定缓存"""
        cache_path = self._get_cache_path(key)
        try:
            if cache_path.exists():
                cache_path.unlink()
            return True
        except Exception as e:
            logger.warning(f"删除缓存失败 {key}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """清空所有缓存"""
        try:
            for f in self.cache_dir.glob("*.parquet"):
                f.unlink()
            logger.info("缓存已清空")
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.stocks_file = self.config_dir / "stocks.json"
        self.settings_file = self.config_dir / "settings.yaml"
    
    def load_stocks(self) -> list:
        """加载自选股列表"""
        if not self.stocks_file.exists():
            return []
        
        try:
            with open(self.stocks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('watchlist', [])
        except Exception as e:
            logger.error(f"加载自选股失败: {e}")
            return []
    
    def save_stocks(self, watchlist: list) -> bool:
        """保存自选股列表"""
        try:
            data = {
                'watchlist': watchlist,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.stocks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存自选股失败: {e}")
            return False
    
    def add_stock(self, code: str, name: str, market: str = "sz") -> bool:
        """添加自选股"""
        watchlist = self.load_stocks()
        
        # 检查是否已存在
        if any(s['code'] == code for s in watchlist):
            logger.info(f"股票 {code} 已在自选列表中")
            return True
        
        watchlist.append({'code': code, 'name': name, 'market': market})
        return self.save_stocks(watchlist)
    
    def remove_stock(self, code: str) -> bool:
        """移除自选股"""
        watchlist = self.load_stocks()
        watchlist = [s for s in watchlist if s['code'] != code]
        return self.save_stocks(watchlist)
    
    def load_settings(self) -> Dict[str, Any]:
        """加载系统设置"""
        default_settings = {
            'refresh_interval': 5,
            'cache_ttl': 300,
            'max_concurrent': 5,
            'default_period': 'daily',
            'adjust_type': 'qfq'
        }
        
        if not self.settings_file.exists():
            return default_settings
        
        try:
            import yaml
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = yaml.safe_load(f) or {}
                return {**default_settings, **settings}
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            return default_settings
