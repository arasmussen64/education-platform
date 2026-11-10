from collections import deque


def count_jobs(job):
    """How many single jobs a job holds: a name is one, a list is the sum of its parts."""
    if isinstance(job, list):
        return 1 + sum(count_jobs(part) for part in job)
    return 1


def run_all(jobs):
    """Run jobs in arrival order; a job that is a list of parts puts its parts at the back of the queue."""
    queue = deque(jobs)
    done = []
    while queue:
        job = queue.popleft()
        if isinstance(job, list):
            queue.extend(job)
        else:
            done.append(job)
    return done


jobs = ["a", ["b", "c"], "d", [["e"], "f"]]
print(count_jobs(jobs))
print(" ".join(run_all(jobs)))
