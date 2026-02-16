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
            or (p.getScope().getName() = "get_profile" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "update_profile_field" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "set_user_theme" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_user_theme_obj" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_posts_for_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_user_home_dir" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "find_class" and p.getParameter().getName() = "module")
            or (p.getScope().getName() = "find_class" and p.getParameter().getName() = "name")
            or (p.getScope().getName() = "safe_unpickle" and p.getParameter().getName() = "data")
            or (p.getScope().getName() = "secure_filename" and p.getParameter().getName() = "filename")
            or (p.getScope().getName() = "validate_image_upload" and p.getParameter().getName() = "filename")
            or (p.getScope().getName() = "check_auth" and p.getParameter().getName() = "password")
            or (p.getScope().getName() = "check_auth" and p.getParameter().getName() = "user_row")
            or (p.getScope().getName() = "hash_password" and p.getParameter().getName() = "password")
            or (p.getScope().getName() = "verify_password" and p.getParameter().getName() = "password")
            or (p.getScope().getName() = "verify_password" and p.getParameter().getName() = "password_hash")
            or (p.getScope().getName() = "create_user" and p.getParameter().getName() = "password")
            or (p.getScope().getName() = "create_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "delete_user" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "promote_to_admin" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "add_post" and p.getParameter().getName() = "content")
            or (p.getScope().getName() = "add_post" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "get_profile" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "update_profile_field" and p.getParameter().getName() = "field")
            or (p.getScope().getName() = "update_profile_field" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "update_profile_field" and p.getParameter().getName() = "value")
            or (p.getScope().getName() = "save_theme" and p.getParameter().getName() = "color")
            or (p.getScope().getName() = "save_theme" and p.getParameter().getName() = "font")
            or (p.getScope().getName() = "save_theme" and p.getParameter().getName() = "name")
            or (p.getScope().getName() = "save_theme" and p.getParameter().getName() = "owner")
            or (p.getScope().getName() = "save_theme" and p.getParameter().getName() = "theme_obj")
            or (p.getScope().getName() = "list_themes_for_user_or_public" and p.getParameter().getName() = "owner")
            or (p.getScope().getName() = "get_theme_by_id" and p.getParameter().getName() = "theme_id")
            or (p.getScope().getName() = "set_user_theme" and p.getParameter().getName() = "theme_id")
            or (p.getScope().getName() = "set_user_theme" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "import_theme" and p.getParameter().getName() = "fileobj")
            or (p.getScope().getName() = "import_theme" and p.getParameter().getName() = "name")
            or (p.getScope().getName() = "import_theme" and p.getParameter().getName() = "owner")
            or (p.getScope().getName() = "get_user_theme_obj" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "is_admin" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "profile" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "download" and p.getParameter().getName() = "filename")
            or (p.getScope().getName() = "download" and p.getParameter().getName() = "username")
            or (p.getScope().getName() = "notify" and p.getParameter().getName() = "username")
        )
    )
    or
    exists(API::CallNode call |
        source = call and (
            (call = API::moduleImport("").getMember("0").getACall() and call.getScope().getName() = "listcomp")
        )
    )
}

// --- SINKS ---
predicate isLLMGeneratedSink(DataFlow::Node sink) {
    exists(API::CallNode call |
        (
            (exists(API::Node n0, API::Node n1, API::Node n2 | n0 = API::moduleImport("sqlite3") and isFuzzyMember(n0, "connect", n1) and isFuzzyMember(n1, "cursor", n2) and call = n2.getMember("execute").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("pickle") and isFuzzyMember(n0, "Unpickler", n1) and call = n1.getMember("load").getACall()))
            or (call = API::moduleImport("pickle").getMember("dumps").getACall())
            or (call = API::moduleImport("os").getMember("makedirs").getACall())
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and call = n1.getMember("join").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and call = n1.getMember("abspath").getACall()))
            or (exists(API::Node n0, API::Node n1, API::Node n2 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and isFuzzyMember(n1, "abspath", n2) and call = n2.getMember("startswith").getACall()))
            or (call = API::moduleImport("os").getMember("listdir").getACall())
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("os") and isFuzzyMember(n0, "path", n1) and call = n1.getMember("exists").getACall()))
            or (exists(API::Node n0, API::Node n1, API::Node n2 | n0 = API::moduleImport("sqlite3") and isFuzzyMember(n0, "connect", n1) and isFuzzyMember(n1, "cursor", n2) and call = n2.getMember("fetchone").getACall()))
            or (exists(API::Node n0, API::Node n1, API::Node n2 | n0 = API::moduleImport("sqlite3") and isFuzzyMember(n0, "connect", n1) and isFuzzyMember(n1, "cursor", n2) and call = n2.getMember("fetchall").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("sqlite3") and isFuzzyMember(n0, "connect", n1) and call = n1.getMember("commit").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("sqlite3") and isFuzzyMember(n0, "connect", n1) and call = n1.getMember("close").getACall()))
            or (call = API::moduleImport("sqlite3").getMember("Binary").getACall())
            or (call = API::moduleImport("requests").getMember("get").getACall())
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("requests") and isFuzzyMember(n0, "get", n1) and call = n1.getMember("status_code").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("requests") and isFuzzyMember(n0, "get", n1) and call = n1.getMember("text").getACall()))
            or (call = API::moduleImport("flask").getMember("send_file").getACall())
            or (call = API::moduleImport("flask").getMember("redirect").getACall())
            or (call = API::moduleImport("flask").getMember("url_for").getACall())
            or (call = API::moduleImport("flask").getMember("flash").getACall())
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("flask") and isFuzzyMember(n0, "session", n1) and call = n1.getMember("get").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("flask") and isFuzzyMember(n0, "Flask", n1) and call = n1.getMember("route").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("flask") and isFuzzyMember(n0, "Flask", n1) and call = n1.getMember("config").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("flask") and isFuzzyMember(n0, "Flask", n1) and call = n1.getMember("run").getACall()))
            or (call = API::moduleImport("builtins").getMember("Exception").getACall())
            or (call = API::moduleImport("builtins").getMember("True").getACall())
            or (call = API::moduleImport("builtins").getMember("False").getACall())
            or (call = API::moduleImport("builtins").getMember("None").getACall())
            or (call = API::moduleImport("builtins").getMember("getattr").getACall())
            or (call = API::moduleImport("builtins").getMember("__import__").getACall())
            or (call = API::moduleImport("builtins").getMember("hasattr").getACall())
            or (call = API::moduleImport("io").getMember("BytesIO").getACall())
            or (call = API::moduleImport("re").getMember("sub").getACall())
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("re") and isFuzzyMember(n0, "sub", n1) and call = n1.getMember("startswith").getACall()))
            or (exists(API::Node n0, API::Node n1, API::Node n2 | n0 = API::moduleImport("re") and isFuzzyMember(n0, "sub", n1) and isFuzzyMember(n1, "rsplit", n2) and call = n2.getMember("lower").getACall()))
            or (exists(API::Node n0, API::Node n1 | n0 = API::moduleImport("re") and isFuzzyMember(n0, "sub", n1) and call = n1.getMember("rsplit").getACall()))
        )
        and sink = call.getArg(_)
    )
}
