
CREATE TABLE poc (
    poc_id  TEXT PRIMARY KEY,
    vul_name TEXT,
    vul_id TEXT,
    vul_type TEXT,
    vul_level TEXT,
    enabled BOOLEAN,
    need_cookie BOOLEAN,
    write_content BOOLEAN,
    created_time TEXT,
    request TEXT,
    payloads TEXT,
    rules TEXT        
)


CREATE TABLE pocscript (
    poc_id  TEXT PRIMARY KEY,
    vul_name TEXT,
    vul_id TEXT,
    vul_type TEXT,
    vul_level TEXT,
    enabled BOOLEAN,
    need_cookie BOOLEAN,
    write_content BOOLEAN,
    created_time TEXT,
    scriptname TEXT     
)