/**
 * @name LLM-Assisted CWE Detecttion
 * @description Detects user-controlled input (Sources) flowing into database lookups (Sinks).
 * @kind path-problem
 * @problem.severity error
 * @id custom/llm-cwes
 */

import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import test_custom_query
import LLMVulnFlow::PathGraph

// 1. Define the Configuration Signature
module LLMVulnConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) { isLLMGeneratedSource(source) }

  predicate isSink(DataFlow::Node sink) { isLLMGeneratedSink(sink) }
  // Optional: Define barriers here if needed (e.g., stopping flow at sanitizers)
  // predicate isBarrier(DataFlow::Node node) { ... }
}

// 2. Instantiate the Global Taint Tracking Module
module LLMVulnFlow = TaintTracking::Global<LLMVulnConfig>;

// 4. Run the Query
from LLMVulnFlow::PathNode source, LLMVulnFlow::PathNode sink
where LLMVulnFlow::flowPath(source, sink)
select sink.getNode(), source, sink, "[LENS] Potential Vulnerability"
