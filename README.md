# Reportable
A simplistic report engine based for Web2py, based totaly on HTML table and Rows objects. 

Add it to your app modules folder and write something like this:

```
  def teste():
      import reportable as rpt

      rows = db(db.cidade.nome.startswith('Pai')).select()

      report = rpt.ReportTable(rows,
                               grouping={'field': 'cidade.uf', 'function': lambda row: row.uf},
                               sumary={'cidade.uf': lambda row, v: v + 1,
                                       'cidade.id': lambda row, v: 'Total de Cidades no Estado'},
                               footer={'Total de Cidades Cadastradas': lambda row, v: v + 1}
                               )

      out = report.generate()
      return dict(report=out)
```

To get something like this:

![Image of Yaktocat](/screenshot.png)

