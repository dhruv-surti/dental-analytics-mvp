import json
import os
import dlt

RAW_DIR = "data/raw"


def load_json_file(filename: str):
    path = os.path.join(RAW_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dlt.resource(name="pms_appointments", write_disposition="replace")
def pms_appointments():
    yield from load_json_file("pms_appointments.json")


@dlt.resource(name="pms_billings", write_disposition="replace")
def pms_billings():
    yield from load_json_file("pms_billings.json")


@dlt.resource(name="finance_collections", write_disposition="replace")
def finance_collections():
    yield from load_json_file("finance_collections.json")


def run_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="dental_ingestion",
        destination="bigquery",
        dataset_name="raw_dental",
    )

    load_info = pipeline.run([
        pms_appointments(),
        pms_billings(),
        finance_collections(),
    ])
    print(load_info)


if __name__ == "__main__":
    run_pipeline()