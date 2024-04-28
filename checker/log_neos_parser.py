import re
import zipfile
import statistics

archive = zipfile.ZipFile("p-033/k-3-n-30-p-033-tr.zip", 'r')


def process_cplex(archive):
    res = list()
    presolve_pattern = re.compile("^Presolve time = (.+) sec. .+$")
    probing_pattern = re.compile("^Probing time = (.+) sec. .+$")
    root_relaxation_pattern = re.compile("^Root relaxation solution time = (.+) sec. .+$")
    total_pattern = re.compile("^Total \\(root\\+branch&cut\\).+ (.+) sec. .+$")
    for name in archive.namelist():
        sec = 0
        lines = archive.read(name).decode("UTF-8").split("\r\n")
        for line in lines:
            if presolve_pattern.match(line):
                x = presolve_pattern.findall(line)
                sec += float(x[0])
            if root_relaxation_pattern.match(line):
                x = root_relaxation_pattern.findall(line)
                sec += float(x[0])
            if probing_pattern.match(line):
                x = probing_pattern.findall(line)
                sec += float(x[0])
            if total_pattern.match(line):
                x = total_pattern.findall(line)
                sec += float(x[0])
        res.append(sec)
    return res


def process_gurobi(archive):
    res = list()
    presolve_pattern = re.compile("^Presolve time: (.+)s$")
    root_relaxation_pattern = re.compile("^Root relaxation: objective .+ (.+) seconds .+$")
    explored_pattern = re.compile("^Explored .+ in (.+) seconds .+")
    for name in archive.namelist():
        sec = 0
        lines = archive.read(name).decode("UTF-8").split("\r\n")
        for line in lines:
            if presolve_pattern.match(line):
                x = presolve_pattern.findall(line)
                sec += float(x[0])
            if root_relaxation_pattern.match(line):
                x = root_relaxation_pattern.findall(line)
                sec += float(x[0])
            if explored_pattern.match(line):
                x = explored_pattern.findall(line)
                sec += float(x[0])
        res.append(sec)
    return res


l = process_cplex(archive)
l = sorted(l)
print(statistics.median(l))
print(statistics.mean(l))
print(statistics.stdev(l))
