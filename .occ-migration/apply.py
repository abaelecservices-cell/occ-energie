#!/usr/bin/env python3
"""Apply a verified, one-time cross-repository migration of OCC Energie blobs."""
from pathlib import Path
import hashlib
import shutil

ROOT = Path("DISTRIBUTION-ELECTRIQUE/OCC-ENERGIE")
PAYLOAD = Path(".occ-migration/payload.txt")
TEMP_WORKFLOW = Path(".github/workflows/occ-consolidation-once.yml")

FILES = [
    ("OCC_ENERGIE.html", "0f558ac669fc1df1f3c3d47c175550c85ac6e85f", "45a5bdb1ab4856cb959d0668d65cdb152aa3b829", 22301, 6189043),
    ("build/data.json", "972f4d3f02a6ec2409f6ab6216aae18216e04af8", "c48580a6a6f005c0494983dc6cf48f54080606f5", 43, 5943067),
]

def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def main() -> None:
    payload = PAYLOAD.read_bytes().decode("utf-8")
    changes = []
    for rel, old_sha, new_sha, prefix, suffix in FILES:
        path = ROOT / rel
        old_raw = path.read_bytes()
        actual = git_blob_sha(old_raw)
        if actual != old_sha:
            raise RuntimeError(f"Source tree changed: {rel}: {actual} != {old_sha}")
        original = old_raw.decode("utf-8")
        patched = original[:prefix] + payload + original[len(original)-suffix:]
        output = patched.encode("utf-8")
        actual_new = git_blob_sha(output)
        if actual_new != new_sha:
            raise RuntimeError(f"SHA mismatch after patch: {rel}: {actual_new} != {new_sha}")
        changes.append((path, output))
    for path, output in changes:
        path.write_bytes(output)
    TEMP_WORKFLOW.unlink()
    shutil.rmtree(PAYLOAD.parent)
    print("SUCCESS: Both large files exactly match the source repository Git SHA.")

if __name__ == "__main__":
    main()
