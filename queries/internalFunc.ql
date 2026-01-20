import python

/** Helper to extract a pretty label for decorators. */
string getDecoratorLabel(Expr d) {
  exists(Call c | c = d | result = getDecoratorLabel(c.getFunc()))
  or
  exists(Attribute a | a = d | result = a.getObject().toString() + "." + a.getName())
  or
  exists(Name n | n = d | result = n.getId())
}

from Function f
where
  // Filter out internal python scopes
  not f.getName().matches("<%>")
select f.getLocation().getFile().getRelativePath() as filename,
  f.getLocation().getStartLine() as linenumber, f.getName() as funcname,
  // 1. Parameters with explicit comma separator
  // Syntax: concat(vars | filter | expression order by i, separator)
  concat(Parameter p, int i | (p = f.getArg(i) and p.getName() != "self") | p.getName(), ", ") as funcparams,
  // 2. Decorators
  concat(Expr d | d = f.getADecorator() | getDecoratorLabel(d), ", ") as decorators,
  // 3. Docstring
  concat(string s | s = f.getDocString().getText() | s, "") as docstring
