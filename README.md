# econicer

This tool enables the analysis of transaction data of a bank account.

The transaction data is analysed for specific keywords and grouped into custom
categories. The grouping information is used to created plots and an automated
report.

## Installation

Install econcier with [pip](https://pypi.org/project/econicer/).
```
pip install econicer
```

### Requirements

At first your bank must provide a function to download all your transaction as
a CSV file, otherwise econcier would be of much use. The CSV file should have
some header information and a table of your transactions with specific fields,
see Section Config Files.

All requirements for Python are found in the 'requirements.txt' file and should
be installed already if you used PyPi.

Furthermore, a Latex installation is needed for the creation of automated
reports. Econicer uses the 'xelatex' compiler. An installation of Miktex
should be sufficient.

### Config Files

Econcier needs 2 separate configuration files for account management. 
* bank.json - describes the structure of the CSV file from your bank
* grouping.json - defines you indented grouping of transactions by specific 
                  data fields

First, the 'bank.json' file contains information of how the file from your bank
is structured. Econicer expects a certain information and you have to specify
where this information can be found in your file.

The other file 'grouping.json' specifies all groups, keywords and fields, which
are searched by econicer.  Single groups are specified by a key, which is follow
by a list of keywords. Econicer uses those keywords to assign a group to every
single transactions. The groups are prioritized, such as the first groups is
preferred over the second. The grouping algorithm will only look into fields,
which are set in the "dbIdentifier" list. 


## Tutorial

The example folder holds all files for the tutorial, but first make sure you
install econicer with pip. The config files are included in the tutorial
folder. Download the tutorial files from the git repo folder 'tutorial'. Copy
all contents from 'tutorial' to a directory, where you want econicer to work.

First, the account has to be initialized by running
```
py -m econicer -i Tutorial
```
This will create the '.db' folder, where eocnicer stores all information.

If you have multiple accounts in the database. After initializing, you can
switch them with
```
py -m econicer -c OtherAccountName
```

For quick look at your current settings run
```
py -m econicer -ls
```

### Adding Transaction Files

After the initialization you can start with adding transaction data to the account.
Make sure, that you are on the correct account before adding the data from your bank.

A example file can be added by
```
py -m econicer -a files\firstFile.csv
```
Econicer reads the file data and merges the current database content with the file.
Add a second file by
```
py -m econicer -a files\secondFile.csv
```

There is the option of undoing the last action with
```
py -m econicer -u
```
but this only works for one step back yet.


### Grouping Transactions

A key feature of econicer is to group your transactions. When you add some data
to your account, econicer will apply the groups defined in the group settings
file. The grouping is used in the later analysis.

The grouping depends on the keyword lists specified in the 'grouping.json' file.
Let's check if all transactions got grouped by
 ```
 py -m econicer -n
```

In this example no all transactions have a groups. You need to be familiar with
editing json files. Let's fix this by add a the keywords 'electricity' and
'supplies' the to 'lining' group in the 'grouping.json' file. Additionally, lets
a new group. The new group can be called 'hobby' with the keyword 'guitar' to
show how much money we spend on our lining hobbies.

Run the regroup command to apply the new grouping settings.
```
py -m econicer -g
```
Now all transactions should have a group assigned.

### Further Analyzing your Transaction History

To analyse the database by searching for a word in the fields. The default field is the 'usage' field.
Fields can be specified as list with the -k flag. Use
```
py -m econicer -s store -k customer usage
```
to search for the word "store" in the fields 'customer' and 'usage'.

### Automated Report and Plots

Finally, Create an automated report with Latex by
```
py -m econicer -r
```

You also can create only the plots for the report, if you don't have Latex.
```
py -m econicer -p
```