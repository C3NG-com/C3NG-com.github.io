# 济南层构科技有限公司

济南层构科技有限公司官方网站。

## 网站结构

```
c3ng.github.io/
├── index.html              # 单页官网（全部内容）
├── assets/
│   ├── favicon.ico         # 多尺寸图标
│   ├── favicon-32.png
│   └── favicon-16.png
├── docs/
│   └── ARCHITECTURE.md     # 项目架构文档
├── CNAME                   # c3ng.com
└── .gitignore
```

单页结构：首屏（公司名 + 业务定位）→ 业务范围 → 联系方式。

## 视觉规范

视觉全部取自品牌规范（`logo/` 那个目录），资源由那份规范生成，**不手工改图**：

| 项 | 取值 |
|---|---|
| 标志 | 三个等距菱形叠放，源文件 `exports/svg/logo-color-on-white.svg` |
| 主色 | Material Blue 300 / 600 / 800：`#64B5F6` `#1E88E5` `#1565C0` |
| 中性色 | slate 一套：`--n50` ~ `--n950`（`#F8FAFC` ~ `#020617`） |
| 字体 | Inter / PingFang SC；英文与数字用 SF Mono |
| 图标 | `exports/favicon/` 直接取用 |

标志的三个面就是三个主色，页面配色只从这里取，不额外加色。样式内联在
`index.html` 里，没有独立的 CSS 文件。

## 内容原则

- **写业务范畴，不写具体产品**：只说「AI 硬件 / 嵌入式软件 / 技术服务」这一层
- **不写具体项目、技术栈、合作方**
- **不用宣传词**：不出现「领先 / 顶尖 / 赋能 / 闭环 / 生态」这类词
- 中英对照用小号等宽英文副标，不做双语大标题

## 本地预览

```bash
python3 -m http.server 8080
```

访问 http://localhost:8080

## 部署

GitHub Pages 从 `main` 分支部署，域名 `c3ng.com`（靠 `CNAME` 文件）。

**推 `main` 即上线。**

## 联系方式

- 邮箱: public@c3ng.com
- 官网: c3ng.com
