import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

# Mock function to simulate extraction
def extract_pdf_mock(pdf_path: Path, output_dir: Path):
    print(f"Start {pdf_path.name}")
    time.sleep(2)
    print(f"End {pdf_path.name}")
    return {"filename": pdf_path.name}

def test_parallelism():
    files = [Path(f"test_{i}.pdf") for i in range(4)]
    output_dir = Path("tmp_out")
    
    print("Testing with 4 workers...")
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(extract_pdf_mock, f, output_dir) for f in files]
        for f in futures:
            f.result()
    end = time.time()
    
    total = end - start
    print(f"Total time: {total:.2f}s")
    if total < 3: # 4 tasks of 2s each in parallel should be ~2s (plus overhead)
        print("Parallelism WORKS")
    else:
        print("Parallelism FAILED")

if __name__ == "__main__":
    test_parallelism()
