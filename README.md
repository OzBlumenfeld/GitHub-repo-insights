# Github repository insights extractor

The purpose of this tool is to extract valuable information of any GitHub repository, although the assignment was focused on a specific repo: CTFd/CTFd.

## Things I would improve but didn't due to time constraints
1. Building the graph runtime is a bit high because I pulled all the commits from master and the branch that I build the graph on.
It can be optimized but didn't have enough the time to do so under the time constraints for this assignment.
2. I would add error handling for various cases of unexpected behavior in code
3. I would add tests to cover core functionality, I did try to run it on multiple inputs but I know it's not enough

## Prerequisites

Before you begin, ensure you have met the following requirements:

* You have installed the latest version of Python and pip.

1. Start a new virtual environment by running the following command in the root directory of the project:
```bash
python -m venv venv
```
2. Install the required packages by running the following command in the root directory of the project:
```bash
pip install -r requirements.txt
```
3. Validate you have Homebrew installed and install graphviz by running the following command:
```bash
brew install graphviz
```

## How to run the tool
1. You can get more info by running the following command:
```bash
python main.py --help
```
2. Run the following command to start the application with default settings
meaning that logging will be to a log file in the logs directory:
```bash
python main.py <token> <owner> <repository>
```
3. Take into account there are the following options:
* --stdout: If you want to see the log in the console
* --debug: If you want to change the log level to DEBUG in order to get more verbose logging

After the above you will:
* Get the repository insights in the log file inside log directory (unless you ran with --stdout flag then the output will be in the console)
* Get the graph dot file
* In order to get the commits graph image you can use the following command:
```bash
dot -Tpng graph.dot -o graph.png
```
### Graph explanation
The graph is a directional graph of some branch that we have indication was merged into master.
The graph starts from the base commit of master and then following the branch first commits up till the merge commit to master.