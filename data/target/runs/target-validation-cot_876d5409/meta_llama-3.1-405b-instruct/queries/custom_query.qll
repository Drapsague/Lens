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
            (p.getScope().getName() = "get_user_by_username" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "create_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "delete_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "promote_to_admin" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "add_post" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_posts_for_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_profile" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "update_profile_field" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "set_user_theme" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_user_theme_obj" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "list_themes_for_user_or_public" and p.getParameter().getName() = "owner")
            or (p.getScope().getName() = "import_theme" and p.getParameter().getName() = "name")
            or (p.getScope().getName() = "import_theme" and p.getParameter().getName() = "owner")
            or (p.getScope().getName() = "get_user_home_dir" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "is_admin" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "profile" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "notify" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "download" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "download" and p.getParameter().getName() = "filename")
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
            (exists(API::Node n0, API::Node n1, API::Node n2 | n0 = API::moduleImport("sqlite3") and isFuzzyMember(n0, "connect", n1) and isFuzzyMember(n1, "cursor", n2) and call = n2.getMember("execute").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("pickle") and isFuzzyMember(n0, "Unpickler", n1) and call = n1.getMember("find_class").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("pickle") and isFuzzyMember(n0, "Unpickler", n1) and call = n1.getMember("load").getACall()))
            or (call = API::moduleImport("os").getMember("makedirs").getACall())
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and call = n1.getMember("join").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and call = n1.getMember("abspath").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and call = n1.getMember("exists").getACall()))
            or (exists(API::Node n0, API::Node n1, API::Node n2 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and isFuzzyMember(n1, "abspath", n2) and call = n2.getMember("startswith").getACall()))
            or (call = API::moduleImport("os").getMember("listdir").getACall())
            or (call = API::moduleImport("flask").getMember("send_file").getACall())
            or (call = API::moduleImport("requests").getMember("get").getACall())
        )
        and sink = call.getArg(_)
    )
}
