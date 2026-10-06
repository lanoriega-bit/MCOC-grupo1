"""Complete DESKTOP pipeline; never invokes AR. Requires --execute to write."""
from pipeline_commands import run
if __name__ == '__main__':
    raise SystemExit(run('rebuild_all'))
