/**
 * AUTO-GENERATED - Generic Chain Support
 */

import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs

/**
 * Helper to match both attributes and method returns.
 * e.g. matches 'obj.prop' AND 'obj.prop()'
 */
predicate isFuzzyMember(API::Node base, string name, API::Node results) {
  results = base.getMember(name)
  or
  results = base.getMember(name).getReturn()
}

// --- SOURCES ---
predicate isLLMGeneratedSource(DataFlow::Node source) {
  exists(DataFlow::ParameterNode p |
    source = p and
    (
      p.getScope().getName() = "show_user" and p.getParameter().getName() = "username"
      or
      p.getScope().getName() = "show_user" and p.getParameter().getName() = "request"
    )
  )
  or
  exists(API::CallNode call |
    source = call and
    (
      call =
        API::moduleImport("flask")
            .getMember("request")
            .getMember("args")
            .getMember("get")
            .getACall() and
      call.getScope().getName() = "com1"
      or
      call =
        API::moduleImport("flask")
            .getMember("request")
            .getMember("args")
            .getMember("get")
            .getACall() and
      call.getScope().getName() = "com2"
      or
      call =
        API::moduleImport("flask")
            .getMember("request")
            .getMember("args")
            .getMember("get")
            .getACall() and
      call.getScope().getName() = "code_ex"
    )
  )
}

// --- SINKS ---
predicate isLLMGeneratedSink(DataFlow::Node sink) {
  exists(API::CallNode call |
    (
      call = API::moduleImport("os").getMember("system").getACall()
      or
      call = API::moduleImport("subprocess").getMember("Popen").getACall()
      or
      call = API::moduleImport("builtins").getMember("exec").getACall()
      or
      call = API::moduleImport("builtins").getMember("eval").getACall()
      or
      exists(API::Node n0, API::Node n1, API::Node n2, API::Node n3 |
        n0 = API::moduleImport("django") and
        isFuzzyMember(n0, "db", n1) and
        isFuzzyMember(n1, "connection", n2) and
        isFuzzyMember(n2, "cursor", n3) and
        call = n3.getMember("execute").getACall()
      )
    ) and
    sink = call.getArg(_)
  )
}
