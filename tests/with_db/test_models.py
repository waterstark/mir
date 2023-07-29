import datetime
import uuid

import pytest
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.database import Base


@pytest.mark.asyncio()
async def test_uuid(session: AsyncSession):
    new_user = {
        "email": "mail@server.com",
        "created_at": datetime.datetime.utcnow(),
        "hashed_password": "pass",
        "is_active": False,
        "is_superuser": False,
        "is_verified": False,
        "is_delete": False,
    }

    # TODO: replace when crud appears
    stmt = insert(AuthUser).values(new_user).returning(AuthUser)
    user = (await session.execute(stmt)).one_or_none()

    assert user is not None
    assert isinstance(user[0].id, uuid.UUID)


@pytest.mark.asyncio()
async def test_table_names_and_columns():
    # import requests
    # from bs4 import BeautifulSoup as BS
    #
    # link = "https://www.postgresql.org/docs/current/sql-keywords-appendix.html"
    #
    # resp = requests.get(link)
    # soup = BS(resp.text, "lxml")
    # table = soup.find("table", class_="table")
    # tbody = table.find("tbody")
    # rows = tbody.find_all("tr")
    #
    # reserved = []
    # non_reserved = []
    #
    # for row in rows:
    #     tds = row.find_all("td")
    #     if tds[1].text == "reserved":
    #         reserved.append(tds[0].text)
    #     if tds[1].text == "non-reserved":
    #         non_reserved.append(tds[0].text)
    #
    # print(reserved)
    # print(non_reserved)

    reserved = ["all", "analyse", "analyze", "and", "any", "asc", "asymmetric", "both", "case", "cast", "check",
                "collate", "column", "constraint", "current_catalog", "current_date", "current_role", "current_time",
                "current_timestamp", "current_user", "default", "deferrable", "desc", "distinct", "do", "else", "end",
                "false", "foreign", "in", "initially", "lateral", "leading", "localtime", "localtimestamp", "not",
                "null", "only", "or", "placing", "primary", "references", "select", "session_user", "some",
                "symmetric", "table", "then", "trailing", "true", "unique", "user", "using", "variadic", "when"]

    non_reserved = ["abort", "absolute", "access", "action", "add", "admin", "after", "aggregate", "also", "alter",
                    "always", "asensitive", "assertion", "assignment", "at", "atomic", "attach", "attribute",
                    "backward", "before", "begin", "breadth", "by", "cache", "call", "called", "cascade", "cascaded",
                    "catalog", "chain", "characteristics", "checkpoint", "class", "close", "cluster", "columns",
                    "comment", "comments", "commit", "committed", "compression", "configuration", "conflict",
                    "connection", "constraints", "content", "continue", "conversion", "copy", "cost", "csv", "cube",
                    "current", "cursor", "cycle", "data", "database", "deallocate", "declare", "defaults", "deferred",
                    "definer", "delete", "delimiter", "delimiters", "depends", "depth", "detach", "dictionary",
                    "disable", "discard", "document", "domain", "double", "drop", "each", "enable", "encoding",
                    "encrypted", "enum", "escape", "event", "exclude", "excluding", "exclusive", "execute", "explain",
                    "expression", "extension", "external", "family", "finalize", "first", "following", "force",
                    "forward", "function", "functions", "generated", "global", "granted", "groups", "handler",
                    "header", "hold", "identity", "if", "immediate", "immutable", "implicit", "import", "include",
                    "including", "increment", "index", "indexes", "inherit", "inherits", "inline", "input",
                    "insensitive", "insert", "instead", "invoker", "isolation", "key", "label", "language", "large",
                    "last", "leakproof", "level", "listen", "load", "local", "location", "lock", "locked", "logged",
                    "mapping", "match", "matched", "materialized", "maxvalue", "merge", "method", "minvalue", "mode",
                    "move", "name", "names", "new", "next", "nfc", "nfd", "nfkc", "nfkd", "no", "normalized",
                    "nothing", "notify", "nowait", "nulls", "object", "of", "off", "oids", "old", "operator",
                    "option", "options", "ordinality", "others", "overriding", "owned", "owner", "parallel",
                    "parameter", "parser", "partial", "partition", "passing", "password", "plans", "policy",
                    "preceding", "prepare", "prepared", "preserve", "prior", "privileges", "procedural", "procedure",
                    "procedures", "program", "publication", "quote", "range", "read", "reassign", "recheck",
                    "recursive", "ref", "referencing", "refresh", "reindex", "relative", "release", "rename",
                    "repeatable", "replace", "replica", "reset", "restart", "restrict", "return", "returns", "revoke",
                    "role", "rollback", "rollup", "routine", "routines", "rows", "rule", "savepoint", "schema",
                    "schemas", "scroll", "search", "security", "sequence", "sequences", "serializable", "server",
                    "session", "set", "sets", "share", "show", "simple", "skip", "snapshot", "sql", "stable",
                    "standalone", "start", "statement", "statistics", "stdin", "stdout", "storage", "stored",
                    "strict", "strip", "subscription", "support", "sysid", "system", "tables", "tablespace", "temp",
                    "template", "temporary", "text", "ties", "transaction", "transform", "trigger", "truncate",
                    "trusted", "type", "types", "uescape", "unbounded", "uncommitted", "unencrypted", "unknown",
                    "unlisten", "unlogged", "until", "update", "vacuum", "valid", "validate", "validator", "value",
                    "version", "view", "views", "volatile", "whitespace", "work", "wrapper", "write", "xml", "yes",
                    "zone"]

    for table in Base.metadata.tables:
        assert table.lower() not in reserved
        assert table.lower not in non_reserved
