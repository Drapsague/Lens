import python
import semmle.python.ApiGraphs

predicate apiPrettyPath(API::Node n, string dotted) {
  exists(string raw, string p1, string p2, string p3, string p4 |
    raw = n.getPath() and
    p1 = raw.regexpReplaceAll("\"([^\"]*)\"", ".$1") and
    p2 = p1.regexpReplaceAll("(\\.?)\\w+\\(", "$1") and
    p3 = p2.regexpReplaceAll("[()]", "") and
    p4 = p3.regexpReplaceAll("\\.+", ".") and
    dotted = p4.regexpReplaceAll("^\\.|\\.$", "")
  )
}

from API::Use u, string pretty
where
  apiPrettyPath(u, pretty) and
  pretty != "self"
select u.getLocation().getFile().getRelativePath() as filename,
  u.getLocation().getStartLine() as linenumber, pretty as extapis
// pretty != "builtins" and
// not pretty.matches("builtins.%")
//predicate apiPrettyPath(API::Node n, string dotted) {
//  exists(string raw, string p1, string p2, string p3, string p4 |
//    raw = n.getPath() and
//    p1 = raw.regexpReplaceAll("\\\"([^\\\"]*)\\\"", ".$1") and
//    p2 = p1.regexpReplaceAll("(\\.?)\\w+\\(", "$1") and
//    p3 = p2.regexpReplaceAll("[()]", "") and
//    p4 = p3.regexpReplaceAll("\\.+", ".") and
//    dotted = p4.regexpReplaceAll("^\\.|\\.$", "")
//  )
//}
//
//from API::Use u, string pretty
//where apiPrettyPath(u, pretty)
//select u.getLocation().getFile().getRelativePath(), u.getLocation().getStartLine(), pretty
