import json
import argparse
import subprocess
import os

def runProcess(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(result.returncode != 0):
        print(("CMD FAILED: %s") % cmd)
    return result

def checkDirectory(path):
    try:
        if os.path.exists(path):
            if os.path.isdir(path):
                return True
        return False
    except FileNotFoundError:
        return False
        
def normalizePath(path):
	return path.replace("\\", "/")

def main():
    parser = argparse.ArgumentParser(description='tool to sync git repos without history')

    parser.add_argument('repo_list_json', help="path to repo list json file")

    parser.add_argument('-v', '--verbose', action='store_true', help='print verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='only process the first 3 repos in the list for debugging purposes')
    parser.add_argument('-l', '--list', action='store_true', help='list all repos, but do nothing')

    args = parser.parse_args()

    with open(args.repo_list_json, 'r', encoding='utf-8') as f:
        data = f.read()

    repos = json.loads(data)

    if args.verbose:
        print("Verbose mode enabled!")

    originalWorkingDirectory = os.getcwd()

    if args.list:
        for repo in repos:
            print(repo["sourceurl"]+" : "+repo["directory"])
        exit(0)

    repoCounter = 0
    for repo in repos:
        if checkDirectory(repo["directory"]) == True:
            
            os.chdir(repo["directory"])
            if args.verbose:
                print("change to "+repo["directory"]+" and fetch")

            cmd = []
            cmd.append("git")
            cmd.append("fetch")
            cmd.append("--depth 1")
            runProcess(cmd)
            
            cmd = []
            cmd.append("git rev-parse --abbrev-ref --symbolic-full-name '@{u}'")
            branch = runProcess(cmd)

            if args.verbose:
                print("reset to branch "+branch)

            cmd = []
            cmd.append("git")
            cmd.append("reset")
            cmd.append("--hard")
            cmd.append(branch)
            runProcess(cmd)

            if args.verbose:
                print("clean")
            cmd = []
            cmd.append("git")
            cmd.append("clean")
            cmd.append("-dfx")
            runProcess(cmd)
            
            os.chdir(originalWorkingDirectory)

        else:
            if args.verbose:
                print("clone "+repo["sourceurl"]+" to "+repo["directory"])

            cmd = []
            cmd.append("git")
            cmd.append("clone")
            cmd.append("--depth 1")
            cmd.append(repo["sourceurl"])
            cmd.append(repo["directory"])

        repoCounter += 1
        if args.debug:
            print("DEBUG MODE, abort after 3 repos")
            os.exit(0)







if __name__ == "__main__":
    main()


# clone by git clone --depth 1 url directory

# update:
#  git fetch --depth 1
#  git reset --hard origin/B
#    git reset --hard "$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}')"
#  git clean -dfx
