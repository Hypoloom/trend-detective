from collections import Counter

from engine import analyze
from validate import synth


def run(n_list=(10, 20, 30, 45), seeds=200, slope=0.03):
    print(f"two regions, slopes +{slope} and -{slope} per year, {seeds} seeds each")
    for n in n_list:
        c = Counter()
        for sd in range(seeds):
            a = synth(n, 2 * sd, slope)
            b = synth(n, 2 * sd + 1, -slope)
            v = analyze((a + b) / 2, regions={"A": a, "B": b})["verdict"].split(" (")[0]
            c[v] += 1
        print(f"  {n:>2} yrs:", ", ".join(f"{k} {100 * x / seeds:.0f}%" for k, x in sorted(c.items())))


if __name__ == "__main__":
    run()