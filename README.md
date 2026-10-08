# P/D 与 PRR 论文阅读室

静态阅读网站：按两组列出论文，直接打开已有中文 PDF，并提供逐篇论文阅读问答。网站通过 GitHub Pages 公开发布，Safari 可直接访问，无需登录。

- 阅读网址：https://micavro.github.io/pd-prr-reading-room/
- GitHub 仓库：https://github.com/micavro/pd-prr-reading-room

PRR 的 [论文与 Kimi 风格问答页面](https://micavro.github.io/pd-prr-reading-room/papers/prr.html) 集中提供 21 页中文全文、12 页 ACM 英文原文，以及《翻译论文并撰写 Kimi 问答》对话中的问答 PDF 和文字版。网页问答为展开讲解版，附件保留该对话导读原稿。首页也提供英文原文直达入口。

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

`content.json` 保存题录、问答和来源。`build_site.py` 只读取其中明确列出的 PDF，复制到 `dist/pdfs/`，生成首页和论文页。不扫描或上传研究工作区。`dist/` 保存已提交的发布快照；预览、打包和其他中间文件保存在忽略目录中。

## 维护

更新内容后重新生成并验证。网页和 PDF 使用稳定的英文文件名。PDF 使用普通 HTTPS 链接，交给 Safari 自带阅读器打开。网页问答与书签使用原生 HTML，不依赖第三方脚本、字体或 PDF 阅读服务。

问答为助手依据论文和现有阅读资料整理，不是 Kimi 服务的实际输出；研究建议与作者结论分别标注。正式发布版会核对每份 PDF 页数、中文字符和 SHA-256。`content.json` 可为论文指定 `original_source` 与 `supplements`；生成器将原文和问答附件复制到相对路径，并在清单中记录文件大小、页数及校验值。验证脚本检查附件完整性和页面入口。

## GitHub Pages

仓库只包含此目录的源文件与经选择的 PDF。修改内容后运行生成和验证，提交更新后的 `dist/` 并推送到 `main`，`.github/workflows/pages.yml` 会自动检查链接和 PDF，然后发布到 GitHub Pages。也可在 Actions 中手动触发部署。不要将整个上级研究工作区加入网站仓库。

工作流采用 [GitHub Pages 官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) 的静态产物发布方式，仓库的 Pages 发布来源设为 GitHub Actions。HTML、样式和 PDF 均由 GitHub Pages 提供，不依赖其他网站托管服务。

## 本版收录范围

P/D 组按现有 `prodag` 研究系列解释：33 篇已完成全文中文翻译，涵盖概率 DAG、Gittins、多阶段调度、LLM 请求与工作流服务；另列 PRR 一篇。共 34 篇、204 个问答。此分组并不声称 33 篇都是专门研究 prefill/decode 分离的论文。

`documents/` 保存经选择的 PDF 副本；源码可独立移动和重建，不依赖原研究目录。`dist/` 是发布快照；本独立站点仓库将其一并保存，方便无构建部署。研究笔记和构建中间文件不包含在发布目录中。
