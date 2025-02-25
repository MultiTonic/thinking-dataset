# flake8: noqa - datatonic - 2025 - apache 2.0
import argparse, os, asyncio, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="[%X]")
l = logging.getLogger(__name__)
async def main(a):
    b = os.path.abspath(a.output)
    d = os.path.join(b, "data")
    c = a.log_dir if a.log_dir else os.path.join(b,"log")
    os.makedirs(d, exist_ok=True); os.makedirs(c, exist_ok=True)
    l.info("Out: %s, Src: %s, Dest: %s, Max: %s, BASE: %s, DATA: %s, LOG: %s", a.output, a.source, a.destination, a.max_workers, b, d, c)
if __name__=="__main__":
    p = argparse.ArgumentParser(description="Generate dark thoughts case studies")
    p.add_argument("--output", default=os.getcwd(), help="Output dir (default: cwd)")
    p.add_argument("--source", default="DataTonic/dark_thoughts_stakeholders_80", help="Source dataset")
    p.add_argument("--destination", default="DataTonic/dark_thoughts_casestudy_r1_scaleway_A0", help="Destination dataset")
    p.add_argument("--max-workers", type=int, default=5, help="Max workers (default:5)")
    p.add_argument("--log-dir", default=None, help="Log dir (default: BASE_DIR/log)")
    a = p.parse_args(); asyncio.run(main(a))
