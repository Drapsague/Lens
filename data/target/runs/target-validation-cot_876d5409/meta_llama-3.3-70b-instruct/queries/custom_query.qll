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
            or (p.getScope().getName() = "create_user" and p.getParameter().getName() = "password")
            or (p.getScope().getName() = "create_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "delete_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "promote_to_admin" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "add_post" and p.getParameter().getName() = "content")
            or (p.getScope().getName() = "add_post" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_posts_for_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_profile" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "update_profile_field" and p.getParameter().getName() = "field")
            or (p.getScope().getName() = "update_profile_field" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "update_profile_field" and p.getParameter().getName() = "value")
            or (p.getScope().getName() = "set_user_theme" and p.getParameter().getName() = "theme_id")
            or (p.getScope().getName() = "set_user_theme" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "list_themes_for_user_or_public" and p.getParameter().getName() = "owner")
            or (p.getScope().getName() = "get_theme_by_id" and p.getParameter().getName() = "theme_id")
            or (p.getScope().getName() = "import_theme" and p.getParameter().getName() = "fileobj")
            or (p.getScope().getName() = "import_theme" and p.getParameter().getName() = "name")
            or (p.getScope().getName() = "import_theme" and p.getParameter().getName() = "owner")
            or (p.getScope().getName() = "get_user_theme_obj" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "secure_filename" and p.getParameter().getName() = "filename")
            or (p.getScope().getName() = "check_auth" and p.getParameter().getName() = "password")
            or (p.getScope().getName() = "check_auth" and p.getParameter().getName() = "user_row")
            or (p.getScope().getName() = "get_user_home_dir" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "validate_image_upload" and p.getParameter().getName() = "filename")
            or (p.getScope().getName() = "find_class" and p.getParameter().getName() = "module")
            or (p.getScope().getName() = "find_class" and p.getParameter().getName() = "name")
            or (p.getScope().getName() = "safe_unpickle" and p.getParameter().getName() = "data")
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
            or (call = API::moduleImport("os").getMember("system").getACall())
            or (call = API::moduleImport("pickle").getMember("loads").getACall())
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and call = n1.getMember("join").getACall()))
            or (call = API::moduleImport("os").getMember("makedirs").getACall())
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and call = n1.getMember("abspath").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("sqlite3") and isFuzzyMember(n0, "connect", n1) and call = n1.getMember("commit").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("pickle") and isFuzzyMember(n0, "Unpickler", n1) and call = n1.getMember("load").getACall()))
        )
        and sink = call.getArg(_)
    )
}
