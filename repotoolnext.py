import json
import argparse
import subprocess
import os
import sys

def runProcess(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(("CMD FAILED: %s") % cmd)
        print(result.stdout)
        print(result.stderr)
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

    parser.add_argument('-s', '--scan', action='store_true', help='scan for github repos not found in the repo json')

    args = parser.parse_args()

    with open(args.repo_list_json, 'r', encoding='utf-8') as f:
        data = f.read()

    repos = json.loads(data)

    if args.verbose:
        print("Verbose mode enabled!")

    originalWorkingDirectory = os.getcwd() + os.sep     # always with an "/" at the end

    if args.list:
        for repo in repos:
            print(repo["sourceurl"]+" : "+repo["directory"])
        exit(0)

    if args.scan:
        foundSomethingNew = False
        for subdir, dirs, files in os.walk(originalWorkingDirectory):
            for dir in dirs:
                if dir == ".git":
                    completePath = subdir + os.sep + dir
                    localPath = completePath[len(originalWorkingDirectory):]
                    localPath = localPath[:len(localPath)-len("/.git")]

                    if len(localPath) > 0:      # skip local directory!
                        if args.verbose:
                            print("check if directory is already in list")

                        localPath = localPath + os.sep

                        alreadyInList = False
                        for item in repos:
                            #print(item)
                            if item['directory'] == localPath:
                                alreadyInList = True

                        if alreadyInList == False:
                            print("NEW REPO: "+localPath)
                            if args.verbose:
                                print("change to path :"+completePath[:len(completePath)-len("/.git")])
                            os.chdir(completePath[:len(completePath)-len("/.git")])

                            cmd = []
                            cmd.append("git")
                            cmd.append("config")
                            cmd.append("--get")
                            cmd.append("remote.origin.url")
                            sourceUrl = runProcess(cmd)
                            if sourceUrl.returncode == 0:
                                newItem = {}
                                newItem['directory'] = localPath
                                newItem['sourceurl'] = sourceUrl.stdout.rstrip()    # remove newline in stdout
                                if args.verbose:
                                    print("new repo to insert: "+str(newItem))
                                repos.append(newItem)
                                foundSomethingNew = True
                            else:
                                print("could not find source url for repo : "+localPath)
                                print("errorcode:"+str(sourceUrl.returncode))
                                print("error:"+sourceUrl.stdout)

                        else:
                            print("already in list: "+localPath)

        os.chdir(originalWorkingDirectory)

        if foundSomethingNew == True:
            with open(args.repo_list_json, 'w', encoding='utf-8') as f:
                json.dump(repos, f, ensure_ascii=False, indent=3, sort_keys=True)
        exit(0)

    repoCounter = 0
    for repo in repos:
        if checkDirectory(repo["directory"]) == True:
            
            os.chdir(repo["directory"])
            if args.verbose:
                print("change to "+repo["directory"]+" and fetch")
                print("current directory:"+os.getcwd())

            cmd = []
            cmd.append("git")
            cmd.append("fetch")
            cmd.append("--depth")
            cmd.append("1")
            runProcess(cmd)
            
            cmd = []
            cmd.append("git")
            cmd.append("rev-parse")
            cmd.append("--abbrev-ref")
            cmd.append("--symbolic-full-name")
            cmd.append("@{u}")
            branch = runProcess(cmd)

            if branch.returncode != 0:
                if args.verbose:
                    print("reset to branch "+branch.stdout)

                cmd = []
                cmd.append("git")
                cmd.append("reset")
                cmd.append("--hard")
                cmd.append(branch.stdout)
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
                print("create destination directory structure")
            os.makedirs(repo["directory"], exist_ok=True)

            if args.verbose:
                print("clone "+repo["sourceurl"]+" to "+repo["directory"])

            cmd = []
            cmd.append("git")
            cmd.append("clone")
            cmd.append("--depth")
            cmd.append("1")
            cmd.append(repo["sourceurl"])
            cmd.append(repo["directory"])
            runProcess(cmd)

        repoCounter += 1
        if repoCounter >= 3:
            if args.debug:
                print("DEBUG MODE, abort after 3 repos")
                exit(0)







if __name__ == "__main__":
    main()


# clone by git clone --depth 1 url directory

# update:
#  git fetch --depth 1
#  git reset --hard origin/B
#    git reset --hard "$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}')"
#  git clean -dfx
