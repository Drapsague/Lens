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
      p.getScope().getName() = "profile" and p.getParameter().getName() = "username"
      or
      p.getScope().getName() = "download" and p.getParameter().getName() = "filename"
      or
      p.getScope().getName() = "notify" and p.getParameter().getName() = "username"
    )
  )
  or
  exists(API::CallNode call |
    source = call and
    (
      call = API::moduleImport("request").getMember("form").getACall() and
      call.getScope().getName() = "register"
      or
      call = API::moduleImport("request").getMember("form").getACall() and
      call.getScope().getName() = "login"
      or
      call = API::moduleImport("request").getMember("files").getACall() and
      call.getScope().getName() = "upload"
      or
      call = API::moduleImport("request").getMember("form").getACall() and
      call.getScope().getName() = "add_post_route"
      or
      call = API::moduleImport("request").getMember("form").getACall() and
      call.getScope().getName() = "admin_promote"
    )
  )
}

// --- SINKS ---
predicate isLLMGeneratedSink(DataFlow::Node sink) {
  exists(API::CallNode call |
    (
      exists(API::Node n0, API::Node n1, API::Node n2 |
        n0 = API::moduleImport("sqlite3") and
        isFuzzyMember(n0, "connect", n1) and
        isFuzzyMember(n1, "cursor", n2) and
        call = n2.getMember("execute").getACall()
      )
      or
      exists(API::Node n0, API::Node n1 |
        n0 = API::moduleImport("pickle") and
        isFuzzyMember(n0, "Unpickler", n1) and
        call = n1.getMember("load").getACall()
      )
      or
      call = API::moduleImport("os").getMember("system").getACall()
      or
      call = API::moduleImport("subprocess").getMember("call").getACall()
    ) and
    sink = call.getArg(_)
  )
}
