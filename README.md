# P/D 与 PRR 论文阅读室

静态阅读网站：按两组列出论文，直接打开已有中文 PDF，并提供逐篇论文阅读问答。所有路径相对站点根目录，可部署到 GitHub Pages 子路径或 Sites。

## 生成与验证

在 `reading-site/` 中运行：

```powershell
npm ci
python -m pip install -r requirements.txt
python -X utf8 build_site.py
python -X utf8 verify_site.py
python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

KaTeX 仅在生成阶段把公式转为原生 MathML；浏览器无需加载 JavaScript、外部字体或数学服务。

`content.json` 保存题录、问答和来源。`build_site.py` 只读取其中明确列出的 PDF，复制到 `dist/pdfs/`，生成首页和论文页。不扫描或上传研究工作区。生成产物、预览和打包文件保存在忽略目录中。

## 维护

更新内容后重新生成并验证。网页和 PDF 使用稳定的英文文件名。PDF 使用普通 HTTPS 链接，交给 Safari 自带阅读器打开。网页问答与书签使用原生 HTML，不依赖第三方脚本、字体或 PDF 阅读服务。

问答为助手依据论文和现有阅读资料整理，不是 Kimi 服务的实际输出；研究建议与作者结论分别标注。正式发布版会核对每份 PDF 页数、中文字符和 SHA-256。

## GitHub Pages

仓库可只包含此目录的源文件与经选择的 PDF。运行生成和验证后，将 `dist/` 作为 Pages 发布目录。可使用 `.github/workflows/pages.yml` 手动触发部署。不要将整个上级研究工作区加入网站仓库。

工作流采用 [GitHub Pages 官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) 的静态产物发布方式，需要先在目标仓库启用 Pages / GitHub Actions。当前网站使用 Sites 私人发布，GitHub 工作流不会自动运行。

## 本版收录范围

P/D 组按现有 `prodag` 研究系列解释：33 篇已完成全文中文翻译，涵盖概率 DAG、Gittins、多阶段调度、LLM 请求与工作流服务；另列 PRR 一篇。共 34 篇、204 个问答。此分组并不声称 33 篇都是专门研究 prefill/decode 分离的论文。

`documents/` 保存经选择的 PDF 副本；源码可独立移动和重建，不依赖原研究目录。`dist/` 是发布快照；本独立站点仓库将其一并保存，方便无构建部署。研究笔记和构建中间文件不包含在发布目录中。
