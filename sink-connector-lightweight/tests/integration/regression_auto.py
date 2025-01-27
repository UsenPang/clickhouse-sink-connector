#!/usr/bin/env python3

import os
import sys
import time

from testflows.core import *


append_path(sys.path, "..")

from integration.helpers.argparser import argparser
from integration.helpers.common import check_clickhouse_version
from integration.helpers.common import create_cluster
from integration.requirements.requirements import *
from integration.tests.steps.steps_global import *


xfails = {
    "schema changes/table recreation with different datatypes": [
        (Fail, "debezium data conflict crash")
    ],
    "schema changes/consistency": [(Fail, "doesn't finished")],
    "primary keys/no primary key": [
        (Fail, "https://github.com/Altinity/clickhouse-sink-connector/issues/39")
    ],
    "delete/no primary key innodb": [(Fail, "doesn't work in raw")],
    "delete/no primary key": [(Fail, "doesn't work in raw")],
    "update/no primary key innodb": [(Fail, "makes delete")],
    "update/no primary key": [(Fail, "makes delete")],
    "/mysql to clickhouse replication/mysql to clickhouse replication auto/truncate/no primary key innodb/{'ReplacingMergeTree'}/*": [
        (Fail, "doesn't work")
    ],
    "/mysql to clickhouse replication/mysql to clickhouse replication auto/truncate/no primary key/{'ReplacingMergeTree'}/*": [
        (Fail, "doesn't work")
    ],
    "/mysql to clickhouse replication/mysql to clickhouse replication auto/truncate/no primary key": [
        (Fail, "doesn't work")
    ],
    "consistency": [(Fail, "doesn't finished")],
    "partition limits": [(Fail, "doesn't ready")],
    "delete/many partition many parts/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "delete/one million datapoints/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "delete/many partition one part/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "delete/one partition one part/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "delete/one partition mixed parts/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "delete/many partition mixed parts/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "delete/parallel/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "update/many partition many parts": [
        (
            Fail,
            "doesn't work without primary key and doesn't insert duplicates of primary key",
        )
    ],
    "update/one million datapoints": [
        (
            Fail,
            "doesn't work without primary key and doesn't insert duplicates of primary key",
        )
    ],
    "update/many partition one part": [
        (
            Fail,
            "doesn't work without primary key and doesn't insert duplicates of primary key",
        )
    ],
    "insert/many partition many parts/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "insert/one million datapoints/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "insert/many partition one part/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "insert/one partition one part/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "insert/one partition mixed parts/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "insert/many partition mixed parts/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "insert/parallel/*_no_primary_key": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "/mysql to clickhouse replication/mysql to clickhouse replication auto/insert/*": [
        (
            Fail,
            "doesn't work without primary key as only last row of insert is replicated",
        )
    ],
    "/mysql to clickhouse replication/mysql to clickhouse replication auto/partitions/*": [
        (
            Fail,
            "https://github.com/Altinity/clickhouse-sink-connector/issues/461",
        )
    ],
}


xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("mysql to clickhouse replication auto")
@Requirements(
    RQ_SRS_030_ClickHouse_MySQLToClickHouseReplication("1.0"),
    RQ_SRS_030_ClickHouse_MySQLToClickHouseReplication_Consistency_Select("1.0"),
    RQ_SRS_030_ClickHouse_MySQLToClickHouseReplication_MySQLVersions("1.0"),
    RQ_SRS_030_ClickHouse_MySQLToClickHouseReplication_MySQLStorageEngines_InnoDB(
        "1.0"
    ),
    RQ_SRS_030_ClickHouse_MySQLToClickHouseReplication_MySQLStorageEngines_ReplicatedReplacingMergeTree(
        "1.0"
    ),
)
@Specifications(SRS030_MySQL_to_ClickHouse_Replication)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    env="env/auto",
    stress=None,
    thread_fuzzer=None,
    collect_service_logs=None,
):
    """ClickHouse regression for MySql to ClickHouse replication with auto table creation."""
    nodes = {
        "clickhouse-sink-connector-lt": ("clickhouse-sink-connector-lt",),
        "mysql-master": ("mysql-master",),
        "clickhouse": ("clickhouse", "clickhouse1", "clickhouse2", "clickhouse3"),
        "bash-tools": ("bash-tools",),
        "zookeeper": ("zookeeper",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    if collect_service_logs is not None:
        self.context.collect_service_logs = collect_service_logs

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            thread_fuzzer=thread_fuzzer,
            collect_service_logs=collect_service_logs,
            stress=stress,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(current_dir(), env),
            caller_dir=os.path.join(current_dir()),
        )

    self.context.cluster = cluster

    self.context.env = env

    self.context.clickhouse_table_engines = ["ReplacingMergeTree"]

    self.context.database = "test"

    if check_clickhouse_version("<21.4")(self):
        skip(reason="only supported on ClickHouse version >= 21.4")

    self.context.node = cluster.node("clickhouse")

    with And("I create test database in ClickHouse"):
        create_database(name="test")
        time.sleep(30)

    with Pool(1) as executor:
        Feature(
            run=load("tests.sanity", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.autocreate", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.insert", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.alter", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.compound_alters", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.parallel_alters", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.truncate", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.deduplication", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.types", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.virtual_columns", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.columns_inconsistency", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.snowflake_id", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.databases", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.table_names", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.is_deleted", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.calculated_columns", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.datatypes", "module"),
            parallel=True,
            executor=executor,
        )
        Feature(
            run=load("tests.retry_on_fail", "module"),
            parallel=True,
            executor=executor,
        )
        join()


if __name__ == "__main__":
    regression()
