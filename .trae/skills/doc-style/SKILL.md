---
name: "doc-style"
description: "固化HTML文档风格规范（配色、字体、布局）。当用户创建/修改HTML文档或要求统一文档风格时调用此skill。"
---

# 文档风格规范 (Doc Style)

本skill定义了统一的HTML文档风格规范，适用于所有项目文档。

## 核心配色方案

| 类型 | 背景色 | 左边框色 | 标题色 | 用途 |
|------|--------|----------|--------|------|
| **info** | `#d1ecf1` | `#17a2b8` | `#0c5460` | 信息/数据/表格 |
| **success** | `#d4edda` | `#28a745` | `#155724` | 完成/正向/分析模块 |
| **warning** | `#fff3cd` | `#ffc107` | `#856404` | 警示/中优先级/技术指标 |
| **danger** | `#f8d7da` | `#dc3545` | `#721c24` | 高优先级/重要/危险 |
| **purple** | `#e2d9f3` | `#6f42c1` | `#6f42c1` | 特殊/模块划分/紫色系 |
| **note** | `#fff3cd` | `#ffc107` | `#856404` | 备注/提示 |
| **layer-box** | 渐变 `#667eea → #764ba2` | - | 白色 | 架构层/紫色渐变 |

## CSS 样式模板

```css
/* 基础样式 */
* { box-sizing: border-box; }
body { 
    font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; 
    max-width: 1300px; 
    margin: 0 auto; 
    padding: 30px 20px; 
    line-height: 1.7; 
    color: #333;
    background: #fafbfc;
}
h1 { color: #1a1a2e; border-bottom: 3px solid #16213e; padding-bottom: 12px; margin-bottom: 25px; font-size: 26px; }
h2 { color: #16213e; border-left: 5px solid #0f3460; padding-left: 15px; margin: 30px 0 15px; font-size: 20px; }
h3 { color: #0f3460; margin: 20px 0 12px; font-size: 16px; }

/* 表格样式 */
table { 
    border-collapse: collapse; 
    width: 100%; 
    margin: 15px 0;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border-radius: 8px;
    overflow: hidden;
}
th, td { border: 1px solid #e0e0e0; padding: 10px 12px; font-size: 14px; }
th { color: white; font-weight: 600; }
tr:nth-child(even) { background-color: #f8f9fa; }
tr:hover { background-color: #f0f4ff; }

/* 彩色表格 */
table.info th { background-color: #17a2b8; }
table.success th { background-color: #28a745; }
table.warning th { background-color: #ffc107; }
table.danger th { background-color: #dc3545; }
table.purple th { background-color: #6f42c1; }

/* 彩色盒子 */
.info-box { background: #d1ecf1; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8; margin: 15px 0; }
.success-box { background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin: 15px 0; }
.warning-box { background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 15px 0; }
.danger-box { background: #f8d7da; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545; margin: 15px 0; }
.purple-box { background: #e2d9f3; padding: 15px; border-radius: 8px; border-left: 4px solid #6f42c1; margin: 15px 0; }
.note-box { background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 15px 0; }

/* 渐变盒子 */
.layer-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; border-radius: 10px; }
.layer-box.light { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.layer-box.green { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }

/* 布局 */
.layout-grid { display: grid; gap: 15px; margin: 15px 0; }
.architecture-diagram { display: flex; flex-direction: column; gap: 12px; margin: 15px 0; }

/* 代码 */
code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: "Consolas", monospace; font-size: 12px; }
        pre { background: #f8f8f8; color: #333; padding: 15px; border-radius: 6px; overflow-x: auto; margin: 15px 0; font-size: 13px; border: 1px solid #e0e0e0; }

/* 组件 */
.component { background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 6px; font-size: 13px; }
.stock-item { background: rgba(255,255,255,0.15); padding: 8px 12px; margin: 6px 0; border-radius: 5px; font-size: 13px; }
```

## 布局规范

### 1. 左右布局 (Sidebar + Main)
```html
<div class="layout-grid" style="grid-template-columns: 220px 1fr;">
    <div class="sidebar">侧边内容</div>
    <div class="main-area">主内容</div>
</div>
```

### 2. 多列布局
```html
<div class="layout-grid" style="grid-template-columns: repeat(4, 1fr);">
    <div class="info-box">内容1</div>
    <div class="warning-box">内容2</div>
    ...
</div>
```

### 3. 架构图布局
```html
<div class="architecture-diagram">
    <div class="layer-box">
        <div class="layer-title">层名称</div>
        <div class="components">
            <span class="component">组件1</span>
            <span class="component">组件2</span>
        </div>
    </div>
    <div class="layer-box light">...</div>
</div>
```

## 配色使用指南

| 场景 | 推荐样式 |
|------|----------|
| 系统概述/目标 | `success-box` |
| 核心功能/信息 | `info-box` |
| 待办事项/警示 | `note-box` / `warning-box` |
| 高优先级 | `danger-box` + `table.danger` |
| 中优先级 | `warning-box` + `table.warning` |
| 低优先级/完成 | `success-box` + `table.success` |
| 架构层/模块 | `layer-box` (渐变) |
| 特殊模块 | `purple-box` + `table.purple` |

## 字体规范

| 元素 | 字号 |
|------|------|
| h1 | 26px |
| h2 | 20px |
| h3 | 16px |
| 正文 | 14px |
| 表格 | 14px (th/td) |
| 代码 | 12px |

## 间距规范

| 元素 | 间距 |
|------|------|
| body padding | 30px 20px |
| h2 margin-top | 30px |
| box padding | 15px |
| box margin | 15px 0 |
| 表格 margin | 15px 0 |

## 注意事项

1. **禁止任何黑底**：所有渐变盒子(layer-box)、深色背景容器内禁止放置任何深色元素
   - 深色容器内只使用白色文字或浅色`component`类
   - `<pre>`代码块必须使用浅色背景 (`#f8f8f8`) 而非深色背景
2. **禁止白底白字**：所有box和表格都要有明确的边框色或背景色
3. **紧凑优先**：表格、列表使用小字号和紧凑padding
4. **表格圆角**：表格添加`border-radius: 8px; overflow: hidden;`
5. **悬停效果**：表格行添加`tr:hover { background-color: #f0f4ff; }`

## 调用时机

当用户出现以下情况时调用本skill：
- 创建新的HTML文档
- 修改现有HTML文档的样式
- 要求"统一文档风格"
- 要求"按照某个文档的风格修改"
- 要求"把文档改成花花绿绿的"
