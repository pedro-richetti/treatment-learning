# A Treatment Learning setup for Business Process Deviance Mining
This repository contains a Python code developed to run an existing treatment learning tool in the context of Business Process Deviance Mining. We also provide data used in experiments with four real-life publicly available datasets to demonstrate how treatment learning performs in business process scenarios.
This code is initially design to run in Windows OS, but with minor changes it can run in other OS as well.

## Requeriments
- Windows 10 machine
- Python 3.6
- Pip
- Virtualenv

## Installation
1. Create a new virtual environment in your local computer, called "logConverter" (the project folder).
2. Clone or Download this repository to your local computer and copy the files to project's folder.
3. Activate the project, by running the script activate.bat located in "Scripts" folder.
4. Load dependency modules by running the command in shell: "pip install -r requirements.txt".
5. Place a copy of tar3.exe in repository's root folder. TAR3 can be downloaded from [Hu's website].(http://www.ece.ubc.ca/~yingh/academic/dispatchTAR3.zip). After decompressing the zip file, you will find tar3.exe is in the bin folder.

## Configuration

### base.cfg
This is the configuration file for TAR3. Please refer to [Hu's original work](http://www.ece.ubc.ca/~yingh/academic/manual.html) to make this configuration. This configuration will be replicated to all discovery strategies activated in the pipeline.

### converterCfg.json
This file controls the setup of the discovery pipeline. The parameters are:
|Parameter | Description |
|-|-|
|boa_discovery| Activates Bag of Activities strategy. Values: {true, false}|
|bigram_discovery| Activates Bigram strategy. Values: {true, false}|
|trigram_discovery| Activates Trigram strategy. Values: {true, false}|
|maximal_repeat_sequence_discovery| Activates Maximal Repeat Sequence strategy. Values: {true, false}|
|maximal_repeat_alphabet_discovery| Activates Maximal Repeat Alphabet strategy. Values: {true, false}|
|declare_discovery| Activates Declare strategy. Values: {true, false}|
|verbose| Activates verbose output. Values: {true, false}|
|user_role_with_event| Concatenates user role with activity name in order to consider both as an event. Values: {true, false}|
|path| Full path to folder with log data. Ex: "C:/Users/username/data/event_log1"|
|event_log_filename| Filename of event data file, in csv format (Ex: "procData.csv"). This file must contain three columns with the following header names: "caseid, event, role"
|instance_attributes_filename| Filename of indicators file, in csv format (Ex: "procIndicator.csv"). his file must contain at least two columns with the following header names: "caseid, class". If available more indicators can be added as new columns to this file, with any arbitrary header names. "class" is the target process instance attribute on which the treatment learner will try to discover treatments that explain deviating behavior. 
|classes| All Possible values of "class" attribute. They must be define as an ordered list, with the worst value fisrt (leftmost item) and the best value at last (rightmost item). Ex:["low", "medium", "high","very high"]|
|tar_rounds| Number of TAR3 rounds desired to run for each discovery strategy. Values: {int > 0} |
|thread_pool_size|Maximum number of parallel threads to run during TAR3 execution. Values: {int > 0} |

## Running
- Run "run_pipeline.bat" file

## Outputs
- The results.csv file stores the treament with the highest lift for each strategy.
- A folder for each strategy is created under "path" with the detailed output of each TAR run.
