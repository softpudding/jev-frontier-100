"""Run the published three-size, three-budget experiment."""
import argparse
from .budget_runner import run
p=argparse.ArgumentParser(prog="jf100")
p.add_argument("--run-id",default="replication")
a=p.parse_args();run(a.run_id)
