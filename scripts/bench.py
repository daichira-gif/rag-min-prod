import time, json, requests

def bench_query(n=10):
    t0 = time.time()
    for _ in range(n):
        r = requests.post("http://localhost:8000/query", json={"query":"What is this project?"})
        r.raise_for_status()
    dt = time.time()-t0
    print(f"{n} queries in {dt:.2f}s -> {n/dt:.2f} RPS")

if __name__ == "__main__":
    bench_query(20)
