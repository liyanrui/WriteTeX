WriteTeX for ConTeXt MkIV
========

本项目从 https://github.com/wanglongqi/WriteTeX 那里 fork 而来，将其 hack 为仅支持 ConTeXt MkIV。由于我对 inkscape 的 extension 机制非常不了解，所以希望 wanglongqi 能够让 WriteTeX 支持 TeX 『编译器』的自定义。

我 hack 过的 WriteTeX 去除了对 PDFtoEDIt 的支持，现在它仅依赖 ConTeXt Minimals 与 pdf2svg。如果不知道怎么安装 ConTeXt Minimals，可参考这里：http://liyanrui.is-programmer.com/2009/10/7/this-is-context-minimals.11971.html

为了便于在 writetex.py 中调用 `context` 命令，可在 /usr/local/bin 目录建立 `ctx` 脚本，内容为：

```bash
#!/bin/bash
source /opt/context/tex/setuptex /opt/context/tex
context $@
```

我 hack 过的 writetex.py 中是使用 `ctx` 将 TeX 文档转化为 PDF 的。

有关 writetex.py 的其他说明，请参考 https://github.com/wanglongqi/WriteTeX

最后，谢谢 wanglongqi 的工作！

