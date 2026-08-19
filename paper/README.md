# Paper build

`TIDE-W26.tex` uses the IEEE conference class. Install an IEEEtran package
that provides `IEEEtran.cls`, together with the LaTeX packages named in the
source preamble. The official IEEE conference templates are available from
<https://www.ieee.org/conferences/publishing/templates.html>.

From this directory, reproduce the retained PDF with:

```bash
pdflatex -interaction=nonstopmode -halt-on-error TIDE-W26.tex
pdflatex -interaction=nonstopmode -halt-on-error TIDE-W26.tex
```

The second pass resolves cross-references. The retained output is US Letter
and remains within the workshop's eight-page maximum.
