/**
* AUTO-GENERATED - Generic Chain Support
*/
import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs

/** * Helper to match both attributes and method returns.
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
        source = p and (
            none()
        )
    )
    or
    exists(API::CallNode call |
        source = call and (
            none()
        )
    )
}

// --- SINKS ---
predicate isLLMGeneratedSink(DataFlow::Node sink) {
    exists(API::CallNode call |
        (
            none()
        )
        and sink = call.getArg(_)
    )
}
