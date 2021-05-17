# econicer

This tool enables the analysis of transaction data of a bank account.

## Installation

Install econcier with pip (not working yer)

### Requirements

All requirements for Python are found in the 'requirements.txt' file.

Furthermore, a Latex installation is needed for the creation of automated
reports. Econicer uses the 'xelatex' compiler.

A installation of Miktex should be sufficient.

### Config Files

Econcier needs 2 separate configuration files for account management. 
* bank.json - describes the structure of the CSV file from your bank
* grouping.json - defines you indented grouping of transactions by specific data fields

## Tutorial

The example folder holds all files for the tutorial, but first make sure you
install econicer with pip. The config files are included in the tutorial folder.
Ownload the tutorial files from the git repo folder 'tutorial'.

First, the account has to be initialized by
```
py -m econicer -i Tutorial
```

If you have multiple accounts in the database, you can switch them with
```
py -m econicer -c OtherAccountName
```

After the initialization you can start with adding transactions data to the account.
Make sure, that you are on the correct account before adding the data.
```
py -m econicer -a files\firstFile.csv
```
Econicer reads the file data and merges the current database content with the file.
Add a second file by
```
py -m econicer -a files\secondFile.csv
```

All transactions are regrouped. 

List all non grouped transactions by
```
py -m econicer -n
```
Edit the config\grouping.json file to also group all non grouped transactions
Run the regroup command to apply the new grouping settings.
```
py -m econicer -g
```

After grouping you can analyse the database by searching for a word in the fields. The default field is the 'usage' field.
Fields can be specified as list with the -k flag. Use
```
py -m econicer -s store -k customer usage
```
to search for the word "store" in the fields 'customer' and 'usage'.

Finally, Create an automated report with Latex by
```
py -m econicer -r
```

You also can create only the plots for the report, if you don't have Latex.
```
py -m econicer -p
```